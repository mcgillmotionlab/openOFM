"""
Author: Claude
ofm2.py - Python port of OFM2.mod (Oxford Foot Model 2, v5.0), originally a
Vicon Nexus BodyLanguage script.

Usage with trial dictionaries
-----------------------------
A trial is a dict {"LANK": (N, 3) array, ..., "header": {...}, "parameters": {...}}
(the layout you get from ezc3d / a C3D reader). Marker arrays are picked out by
shape; unlabelled "*nn" trajectories and the header/parameters blocks are
ignored. TravelDirectionX, IS_STATIC and the point units are read from
data["parameters"].

    ofm = OFM2.from_dict(static_trial)          # reads TravelDirectionX etc.
    ofm.run_dict(static_trial, static=True)     # computes and stores the PARAMs
    results = ofm.run_dict(dynamic_trial)       # reuses the stored PARAMs
    trial_plus = {**dynamic_trial, **results}   # results: (N, 3) arrays keyed by name

A dynamic trial can only be processed after a static trial (or load_params),
exactly as in Nexus. Plain marker dicts still work through run(markers, static).
Missing markers can be left out or NaN; sections whose markers are absent are
skipped, mirroring OptionalPoints / ExistAtAll in the original.

CONVENTIONS INFERRED FROM THE SCRIPT (BodyLanguage does not define them in the
.mod file). All of them live in segment() and bl_angles(); check them against
Nexus output on a known trial before relying on the numbers:
  * segment(O, A, B, "abc"): axis a = A, axis b = B x A, axis c completes a
    right-handed set.
  * <A, B, yxz>: Cardan angles of B relative to A (R = A^T B), intrinsic
    Y-X-Z, degrees, sign-reversed relative to the usual right-hand-rule
    extraction. This sign was chosen so that the "+90" offsets in the script
    bring a neutral foot to ~0.
  * Marker sets are in mm, Z up.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np

_AX = {"x": 0, "y": 1, "z": 2}
_EVEN = {(0, 1, 2), (1, 2, 0), (2, 0, 1)}


# --------------------------------------------------------------------------
# Geometry primitives (the BodyLanguage built-ins)
# --------------------------------------------------------------------------

# Equivalent to make unit
def unit(v):
    with np.errstate(invalid="ignore", divide="ignore"):
        return v / np.linalg.norm(v, axis=-1, keepdims=True)


@dataclass
class Segment:
    origin: np.ndarray  # (N, 3)
    R: np.ndarray       # (N, 3, 3); columns are the x, y, z axes

    def axis(self, k):
        """1(seg), 2(seg), 3(seg) in BodyLanguage -> k = 1, 2, 3."""
        return self.R[:, :, k - 1]

# Somewhat equivalent
def segment(origin, a, b, order="xyz"):
    """[origin, a, b, order]"""
    first, second, third = (_AX[c] for c in order)
    u1 = unit(a)
    u2 = unit(np.cross(b, a))
    u3 = np.cross(u1, u2) if (first, second, third) in _EVEN else np.cross(u2, u1)
    R = np.empty((len(origin), 3, 3))
    R[:, :, first], R[:, :, second], R[:, :, third] = u1, u2, u3
    return Segment(origin, R)


def to_local(p, seg):
    """P/Seg : point in the segment's local coordinates."""
    return np.einsum("nji,nj->ni", seg.R, p - seg.origin)


def to_global(local, seg):
    """local * Seg : local (3,) vector back to global coordinates."""
    return seg.origin + np.einsum("nij,j->ni", seg.R, local)


def normal(p2, p3, p4):
    """NORM(p2, p3, p4): unit normal of the plane through three points."""
    return unit(np.cross(p3 - p2, p4 - p2))


def projn(p1, p2, p3, p4):
    """PROJN macro: projection of p1 onto the plane through p2, p3, p4.

    The macro's mirrorP1 / PERP steps reduce to this (p3 lies in the plane, so
    the foot of the perpendicular from p3 onto the line through p1 along the
    normal is the projection of p1). $VECTOR_OFFSET cancels out.
    """
    n = normal(p2, p3, p4)
    return p1 - ((p1 - p3) * n).sum(-1, keepdims=True) * n


def bl_angles(parent, child):
    """<parent, child, yxz> in degrees, shape (N, 3)."""
    R = np.einsum("nji,njk->nik", parent.R, child.R)  # parent^T child
    a = np.arctan2(R[:, 0, 2], R[:, 2, 2])
    b = -np.arcsin(np.clip(R[:, 1, 2], -1.0, 1.0))
    c = np.arctan2(R[:, 1, 0], R[:, 1, 1])
    return -np.degrees(np.stack([a, b, c], axis=-1))


def _mean(x):
    return np.nanmean(x, axis=0)


# --------------------------------------------------------------------------
# Reading a trial dictionary
# --------------------------------------------------------------------------
def _first(parameters, group, name, default=None):
    """parameters[group][name]["value"][0], or default if it isn't there."""
    try:
        value = parameters[group][name]["value"]
        return value[0] if len(value) else default
    except (KeyError, TypeError, IndexError):
        return default


def markers_from_dict(data):
    """Marker trajectories {name: (N, 3) float array} from a trial dictionary.

    Skips "header", "parameters" and unlabelled "*nn" trajectories, and strips a
    "Subject:" prefix from the labels if there is one.
    """
    markers = {}
    for key, val in data.items():
        if key in ("header", "parameters") or str(key).startswith("*"):
            continue
        try:
            arr = np.asarray(val, dtype=float)
        except (TypeError, ValueError):
            continue
        if arr.ndim == 2 and arr.shape[1] == 3:
            markers[str(key).split(":")[-1]] = arr
    if not markers:
        raise ValueError("no (N, 3) marker arrays found in the trial dictionary")
    if len({len(v) for v in markers.values()}) != 1:
        raise ValueError("marker arrays have different numbers of frames")
    return markers


# --------------------------------------------------------------------------
# Output angle table.
# name: (parent, child, c1, c2, c3, offset) for the LEFT foot. The right foot
# uses the same row with c2 and c3 sign-flipped, which is exactly how the
# L and R lines of the script differ.
# Result = [c1*raw1 + offset, c2*raw2, c3*raw3], raw = -<parent, child, yxz>.
# --------------------------------------------------------------------------
ANGLE_TABLE = {
    "TibiaGlobalAngles2":         ("lab",       "tibia",       +1, -1, -1, 0),
    "FootTibiaAngles2":           ("tibia",     "wholefoot",   -1, +1, -1, 90),
    "HindfootTibiaAngles2":       ("tibia",     "hindfoot",    -1, +1, -1, 90),
    "HindfootGlobalAngles2":      ("lab",       "hindfoot",    -1, -1, -1, 90),
    "ForefootHindfootAngles2":    ("hindfoot",  "forefoot",    -1, +1, -1, 0),
    "MedForefootHindfootAngles2": ("hindfoot",  "medforefoot", -1, +1, -1, 0),
    "LatForefootHindfootAngles2": ("hindfoot",  "latforefoot", -1, +1, -1, 0),
    "IntForefootHindfootAngles2": ("hindfoot",  "intforefoot", -1, +1, -1, 0),
    "ForefootTibiaAngles2":       ("tibia",     "forefoot",    -1, +1, -1, 90),
    "HalluxForefootAngles2":      ("forefoot",  "hallux",      -1, +1, -1, 0),
}


class OFM2:
    AXIS_LENGTH = 50.0  # $AXIS_LENGTH

    def __init__(self, travel_direction_x=False, no_wedge_nf=None):
        """
        travel_direction_x : $TravelDirectionX (True if walking along lab X)
        no_wedge_nf        : {"L": bool, "R": bool}  ($LNoWedgeNF / $RNoWedgeNF,
                             historical "not flat, no wedge" data only)
        """
        self.travel_direction_x = travel_direction_x
        self.no_wedge_nf = {"L": False, "R": False}
        self.no_wedge_nf.update(no_wedge_nf or {})
        self.params = {}  # the PARAM store: written by static runs, read by dynamic

    @classmethod
    def from_dict(cls, data):
        """Subject settings from data["parameters"]["PROCESSING"] (PRF values).

        Reads TravelDirectionX, and LNoWedgeNF / RNoWedgeNF if present; anything
        missing defaults to 0, as an unset PRF value would.
        """
        p = data.get("parameters", {})

        def flag(name):
            return bool(_first(p, "PROCESSING", name, 0))

        return cls(travel_direction_x=flag("TravelDirectionX"),
                   no_wedge_nf={"L": flag("LNoWedgeNF"), "R": flag("RNoWedgeNF")})

    # ------------------------------------------------------------------ main
    def run(self, markers, static=False, include_axes=False):
        if not static and not self.params:
            raise ValueError("No static parameters stored. Process a static trial "
                             "first (static=True), or call load_params().")
        m = {k: np.array(v, dtype=float) for k, v in markers.items()}
        n = len(next(iter(m.values())))
        out = {}

        lab = self.define_lab(m, n)
        for side in ("R", "L"):
            segs = self._process_side(side, m, lab, static, include_axes, out)
            self._angles(side, segs, out)
        return out

    def run_dict(self, data, static=None, include_axes=False):
        """run() on a trial dictionary. static=None uses SUBJECTS/IS_STATIC."""
        markers = markers_from_dict(data)
        p = data.get("parameters", {})

        units = str(_first(p, "POINT", "UNITS", "mm")).strip().lower()
        scale = {"mm": 1.0, "cm": 10.0, "m": 1000.0}.get(units)
        if scale is None:
            raise ValueError(f"unsupported point units {units!r} (need mm, cm or m)")
        if scale != 1.0:
            markers = {k: v * scale for k, v in markers.items()}

        if static is None:
            static = bool(_first(p, "SUBJECTS", "IS_STATIC", 0))

        out = self.run(markers, static=static, include_axes=include_axes)

        missing = [S + n for S in ("L", "R") if S + "ANK" in markers
                   for n in (*ANGLE_TABLE, "MedLongArchAngles2") if S + n not in out]
        if missing:
            warnings.warn("not computed (markers or parameters missing): "
                          + ", ".join(missing))
        return out

    # ------------------------------------------------------------ utilities
    @staticmethod
    def _exists(m, name):
        """ExistAtAll(name)"""
        return name in m and bool(np.isfinite(m[name]).any())

    def define_lab(self, m, n):
        """LAB: global frame with x along the direction of travel."""
        side = "R" if self._exists(m, "RANK") else "L"
        ank, hee = m[side + "ANK"], m[side + "HEE"]
        k = 0 if self.travel_direction_x else 1
        direction = np.zeros((n, 3))
        direction[:, k] = np.where(ank[:, k] > hee[:, k], 1.0, -1.0)
        up = np.broadcast_to(np.array([0.0, 0.0, 1.0]), (n, 3))
        return segment(np.zeros((n, 3)), direction, up, "xyz")

    def _axes(self, out, name, origin, seg, neg_x):
        L = self.AXIS_LENGTH
        out[name + "0"] = origin
        out[name + "1"] = origin + (-L if neg_x else L) * seg.axis(1)
        out[name + "2"] = origin + L * seg.axis(2)
        out[name + "3"] = origin + L * seg.axis(3)

    # ------------------------------------------------------- per-side model
    def _process_side(self, S, m, lab, static, include_axes, out):
        P = self.params
        sgn = 1.0 if S == "L" else -1.0  # mirrors the L/R vector flips in the script
        n = len(lab.origin)

        def has(*names):
            return all(self._exists(m, S + nm) for nm in names)

        def g(name):
            return m[S + name]

        segs = {"lab": lab}

        # ===== Tibia ======================================================
        ofm_ajc = None
        if has("ANK", "HFB", "SHN"):
            ank = g("ANK")
            dummy_tib = segment(ank, g("HFB") - ank,
                                g("SHN") - (ank + g("HFB")) / 2)
            if static and has("MMA"):
                P[S + "MMA_2"] = _mean(to_local(g("MMA"), dummy_tib))
            if S + "MMA_2" in P:
                m[S + "MMA"] = to_global(P[S + "MMA_2"], dummy_tib)
                ofm_ajc = (ank + g("MMA")) / 2

        if ofm_ajc is not None:
            # KJC: functional (1), model/PiG (2), or tibia markers only (3)
            if has("KJCFunc"):
                kjc, model = g("KJCFunc"), 1
            elif has("KJC"):
                kjc, model = g("KJC"), 2
            elif has("TUB"):
                kjc, model = projn(g("TUB"), g("ANK"), g("MMA"), g("HFB")), 3
            else:
                kjc, model = None, None
            if kjc is not None:
                if model == 3:
                    ajc = ofm_ajc
                elif has("AJC"):
                    ajc = g("AJC")  # PiG ankle joint centre
                else:
                    raise ValueError(f"{S}AJC (from PiG) is needed when the knee "
                                     f"centre comes from {S}KJC/{S}KJCFunc")
                if static:
                    P[S + "KneeModel"] = model
                out[S + "KJC"] = kjc
                segs["tibia"] = segment(ofm_ajc, kjc - ajc,
                                        sgn * (g("ANK") - ajc), "zxy")
                if include_axes:
                    self._axes(out, S + "TIB", ofm_ajc, segs["tibia"], neg_x=False)

        # ===== Hindfoot ===================================================
        heemla = None
        if has("HEE", "STL", "LCA"):
            hee = g("HE1") if has("HE1") else g("HEE")  # undo an OFM1 shift
            if has("HE1"):
                out[S + "HEE"] = hee
            heeorig = g("HEEorig") if has("HEEorig") else hee.copy()
            stl, lca = g("STL"), g("LCA")
            dummy_hf = segment(hee, hee - (stl + lca) / 2, stl - lca)

            toeproj = d1mproj = None
            use_wedge = False
            if static and has("P1M", "P5M", "D1M", "D5M", "TOE", "PCA"):
                p1p5mid = (g("P1M") + g("P5M")) / 2
                heemid = (stl + lca) / 2
                rearfoot = segment(heemid, p1p5mid - heemid,
                                   sgn * (lca - stl), "yzx")
                rearfoot_prox = heemid - 20 * rearfoot.axis(3)
                # project HEE medially/laterally into the midline of the rear/mid foot
                heelatproj = projn(hee, p1p5mid, heemid, rearfoot_prox)
                out[S + "RearFootProx"] = rearfoot_prox
                out[S + "HEElatproj"] = heelatproj

                d1m, d5m, toe = g("D1M"), g("D5M"), g("TOE")
                if self.no_wedge_nf[S]:
                    # historical data: plane of HEE, D5M, D1M
                    heeproj = projn(heelatproj, heelatproj, d5m, d1m)
                    stlproj = projn(stl, heelatproj, d5m, d1m)
                    lcaproj = projn(lca, heelatproj, d5m, d1m)
                elif has("Wedge1", "Wedge2", "Wedge3"):
                    w = (g("Wedge1"), g("Wedge2"), g("Wedge3"))
                    heeproj = projn(heelatproj, *w)
                    stlproj = projn(stl, *w)
                    lcaproj = projn(lca, *w)
                    toeproj = projn(toe, *w)
                    d1mproj = projn(d1m, *w)
                    use_wedge = True
                else:
                    floor = (np.array([0.0, 0.0, 0.0]), np.array([0.0, 100.0, 0.0]),
                             np.array([100.0, 0.0, 0.0]))
                    heeproj = projn(heelatproj, *floor)
                    stlproj = projn(stl, *floor)
                    lcaproj = projn(lca, *floor)

                P[S + "UseWedge"] = use_wedge
                P[S + "HEEproj"] = _mean(to_local(heeproj, dummy_hf))
                P[S + "STLproj"] = _mean(to_local(stlproj, dummy_hf))
                P[S + "LCAproj"] = _mean(to_local(lcaproj, dummy_hf))
                P[S + "PCA"] = _mean(to_local(g("PCA"), dummy_hf))

                # lateral offset between the ankle joint centre and the rearfoot midline
                if ofm_ajc is not None:
                    ajcproj = projn(ofm_ajc, heeproj, stlproj, lcaproj)
                    ajcsag = projn(ajcproj, p1p5mid, heemid, rearfoot_prox)
                    P[S + "HeelTrans"] = _mean(np.linalg.norm(ajcproj - ajcsag, axis=-1))

                # ---- PiG compatibility: shift HEE to the height of TOE --------
                if self.no_wedge_nf[S]:
                    hee_new = (heeorig + g("PCA")) / 2
                    heemla_s = heeorig
                elif use_wedge:
                    # same distance from the wedge as TOE / D1M, on the same side
                    hee_new = heeproj + (toe - toeproj)
                    heemla_s = heeproj + (d1m - d1mproj)
                else:  # foot assumed flat on the floor
                    hee_new = hee.copy()
                    hee_new[:, 2] = toe[:, 2]
                    heemla_s = hee.copy()
                    heemla_s[:, 2] = d1m[:, 2]
                P[S + "HEEmla"] = _mean(to_local(heemla_s, dummy_hf))
                P[S + "HEEoffset"] = _mean(np.linalg.norm(heeorig - hee_new, axis=-1))
                out[S + "HEEorig"] = heeorig
                out[S + "HEE"] = hee_new
                out[S + "HEEmla"] = heemla_s
                m[S + "HEE"] = hee_new  # shifted HEE is used from here on

            if S + "HEEproj" in P and S + "PCA" in P:
                heeproj = to_global(P[S + "HEEproj"], dummy_hf)
                stlproj = to_global(P[S + "STLproj"], dummy_hf)
                lcaproj = to_global(P[S + "LCAproj"], dummy_hf)
                pca = to_global(P[S + "PCA"], dummy_hf)
                hfmid = (stlproj + lcaproj) / 2
                segs["hindfoot"] = segment(heeproj, hfmid - heeproj,
                                           pca - heeorig, "zyx")
                if include_axes:
                    self._axes(out, S + "HDF", heeproj, segs["hindfoot"], neg_x=True)
            if S + "HEEmla" in P:
                heemla = to_global(P[S + "HEEmla"], dummy_hf)

        # ===== Whole foot =================================================
        if has("HEE", "TOE", "D5M") and (has("D1M") or S + "D1Mfoot" in P):
            hee, toe, d5m = g("HEE"), g("TOE"), g("D5M")
            dummy_wf = segment(hee, hee - toe, sgn * (toe - d5m), "zxy")
            if static and has("D1M"):
                P[S + "D1Mfoot"] = _mean(to_local(g("D1M"), dummy_wf))
            d1mfoot = to_global(P[S + "D1Mfoot"], dummy_wf)
            out[S + "D1Mfoot"] = d1mfoot
            segs["wholefoot"] = segment(hee, toe - hee, sgn * (d5m - d1mfoot), "zxy")

        # ===== Midfoot: D1M from the forefoot, then medial longitudinal arch ==
        if has("P1M", "P5M", "D5M", "TOE") and (has("D1M") or S + "D1M_ff" in P):
            dummy_ff = segment(g("P1M"), g("P1M") - g("D5M"), g("TOE") - g("P5M"))
            if static and has("D1M"):
                P[S + "D1M_ff"] = _mean(to_local(g("D1M"), dummy_ff))
            m[S + "D1M"] = to_global(P[S + "D1M_ff"], dummy_ff)

        if has("NAV", "P5M", "D1M") and heemla is not None:
            nav, p5m, d1m = g("NAV"), g("P5M"), g("D1M")
            prox = segment(heemla, nav - heemla, sgn * (p5m - nav), "zxy")
            dist = segment(d1m, d1m - nav, sgn * (p5m - nav), "zxy")
            mla = bl_angles(dist, prox)  # <dist, prox, yxz>, no leading '-' in the script
            out[S + "MedLongArchAngles2"] = np.stack(
                [mla[:, 0] - 180, mla[:, 1], -mla[:, 2]], axis=-1)

        # ===== Forefoot, medial/lateral/intermediate forefoot, hallux =====
        if has("P1M", "P5M", "D1M", "D5M", "TOE"):
            p1m, p5m, d1m, d5m, toe = (g(k) for k in ("P1M", "P5M", "D1M", "D5M", "TOE"))
            p1mproj = projn(p1m, d1m, d5m, p5m)
            toeproj_ff = projn(toe, d1m, d5m, p5m)
            ffmid = (p1mproj + p5m) / 2
            segs["forefoot"] = segment(toeproj_ff, toeproj_ff - ffmid,
                                       sgn * (d5m - d1m), "zxy")
            if include_axes:
                self._axes(out, S + "FOF", toeproj_ff, segs["forefoot"], neg_x=True)

            if has("P23M"):
                prox_pt = (p1m + g("P23M")) / 2
                dist_pt = (d1m + toe) / 2
                segs["medforefoot"] = segment(prox_pt, dist_pt - prox_pt,
                                              sgn * (toe - d1m), "zxy")
            if has("D4M"):
                segs["latforefoot"] = segment(p5m, d5m - p5m,
                                              sgn * (d5m - g("D4M")), "zxy")
                if has("P23M"):
                    segs["intforefoot"] = segment(g("P23M"), toe - g("P23M"),
                                                  sgn * (g("D4M") - toe), "zxy")
            if has("HLX"):
                segs["hallux"] = segment(d1m, g("HLX") - d1m, sgn * (d5m - d1m), "zxy")
                if include_axes:
                    self._axes(out, S + "HLX", g("HLX"), segs["hallux"], neg_x=True)

        return segs

    # ------------------------------------------------------- output angles
    def _angles(self, S, segs, out):
        sgn = 1.0 if S == "L" else -1.0
        for name, (parent, child, c1, c2, c3, off) in ANGLE_TABLE.items():
            if parent in segs and child in segs:
                raw = -bl_angles(segs[parent], segs[child])  # -<parent, child, yxz>
                out[S + name] = np.stack(
                    [c1 * raw[:, 0] + off, sgn * c2 * raw[:, 1], sgn * c3 * raw[:, 2]],
                    axis=-1)