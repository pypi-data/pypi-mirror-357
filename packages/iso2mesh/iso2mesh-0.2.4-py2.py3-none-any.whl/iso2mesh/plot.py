"""@package docstring
Iso2Mesh for Python - Primitive shape meshing functions

Copyright (c) 2024-2025 Qianqian Fang <q.fang at neu.edu>
"""

__all__ = [
    "plotsurf",
    "plotasurf",
    "plotmesh",
    "plotedges",
    "plottetra",
]

##====================================================================================
## dependent libraries
##====================================================================================

import numpy as np
import matplotlib.pyplot as plt
from iso2mesh.trait import volface, meshcentroid

# _________________________________________________________________________________________________________


def plotsurf(node, face, *args, **kwargs):
    rngstate = np.random.get_state()
    h = []

    randseed = int("623F9A9E", 16)

    if "ISO2MESH_RANDSEED" in globals():
        randseed = globals()["ISO2MESH_RANDSEED"]
    np.random.seed(randseed)

    if isinstance(face, list):  # polyhedral facets
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        from matplotlib.patches import Polygon

        sc = np.random.rand(10, 3)
        newsurf = {}
        for fc in face:
            if (
                isinstance(fc, (list, tuple))
                and len(fc) >= 2
                and isinstance(fc[0], (list, tuple))
            ):
                group_id = fc[1][0]
                if group_id + 1 > sc.shape[0]:
                    sc = np.vstack([sc, np.random.rand(group_id + 1 - sc.shape[0], 3)])
                newsurf.setdefault(group_id, []).append(np.asarray(fc[0]) - 1)
            else:
                newsurf.setdefault(1, []).append(np.asarray(fc) - 1)

        ax = plt.gca()

        if ax.name != "3d":
            plt.figure()  # Create a new figure
            ax = plt.gcf().add_subplot(
                projection="3d"
            )  # Add 3D axes to the current figure

        poly3d = [
            node[np.array(subf).flatten(), :3]
            for subface in newsurf.values()
            for subf in subface
        ]
        colmap = [sc[i - 1, :] for i, subface in newsurf.items() for subf in subface]

        patch = Poly3DCollection(poly3d, facecolors=colmap, edgecolors="k", **kwargs)
        ax.add_collection3d(patch)
        _autoscale_3d(ax, node)
        h.append(patch)

    else:
        if face.shape[1] == 4:
            tag = face[:, 3]
            types = np.unique(tag)
            # plt.hold(True)
            h = []
            for i in range(len(types)):
                if node.shape[1] == 3:
                    h.append(
                        plotasurf(
                            node,
                            face[tag == types[i], 0:3],
                            *args,
                            **kwargs,
                        )
                    )
                else:
                    h.append(
                        plotasurf(node, face[tag == types[i], 0:3], *args, **kwargs)
                    )
        else:
            h = plotasurf(node, face, *args, **kwargs)

    #        if np.all(np.array(plt.gca().view) == [0, 90]):
    #            plt.view(3)

    np.random.set_state(rngstate)
    # plt.axis("equal")

    return h


# _________________________________________________________________________________________________________


def plotasurf(node, face, *args, **kwargs):
    if face.shape[1] <= 2:
        ax = plotedges(node, face, *args, **kwargs)
    else:
        ax = plt.gca()

        if ax.name != "3d":
            plt.figure()  # Create a new figure
            ax = plt.gcf().add_subplot(
                projection="3d"
            )  # Add 3D axes to the current figure

        if not "color" in kwargs and not "cmap" in kwargs:
            kwargs["cmap"] = plt.get_cmap("jet")
        if not "edgecolor" in kwargs:
            kwargs["edgecolor"] = "k"
        trisurf = ax.plot_trisurf(
            node[:, 0],
            node[:, 1],
            node[:, 2],
            triangles=face - 1,
            **kwargs,
        )
        if node.shape[1] == 4:
            trisurf.set_array(node[:, 3])
            trisurf.autoscale()
        _autoscale_3d(ax, node)

    if "trisurf" in locals():
        return trisurf


# _________________________________________________________________________________________________________


def plottetra(node, elem, *args, **kwargs):
    """
    hm = plottetra(node, elem, *args, **kwargs)

    Plot 3D surface meshes.

    Parameters:
        node: (N, 3) or (N, 4) array of node coordinates (last column optional for color).
        elem: (M, 4) or (M, 5) array of tetrahedra (last column optional for tags).
        args, kwargs: Additional plotting options passed to plotsurf.

    Returns:
        hm: list of plot handles.
    """

    # Save current RNG state
    rngstate = np.random.get_state()

    # Set deterministic seed for consistent coloring
    randseed = int("623F9A9E", 16)

    if "ISO2MESH_RANDSEED" in globals():
        randseed = globals()["ISO2MESH_RANDSEED"]

    np.random.seed(randseed)

    h = []

    if not isinstance(elem, list):
        if elem.shape[1] > 4:
            tag = elem[:, 4]  # 1-based -> column 5 in MATLAB
            types = np.unique(tag)
            for t in types:
                idx = np.where(tag == t)[0]
                face = volface(elem[idx, :4])[
                    0
                ]  # Pass only first 4 columns (1-based in MATLAB)
                kwargs["color"] = np.random.rand(1, 3)
                h.append(plotsurf(node, face, *args, **kwargs))
        else:
            face = volface(elem[:, :4])[0]
            h.append(plotsurf(node, face, *args, **kwargs))

    # Restore RNG state
    np.random.set_state(rngstate)

    # Return handle if needed
    if h:
        return h


# _________________________________________________________________________________________________________


def plotedges(node, edges, *args, **kwargs):
    """
    Plot a 3D polyline or closed loop (1D manifold).

    Parameters
    ----------
    node : ndarray (N, 3 or 4)
        Node coordinates. If a 4th column is present, it can represent color.
    edges : ndarray or list
        Either a 2-column edge list or a 1D list/array of node indices separated by NaN.
    *args : list
        Additional plotting options (passed to matplotlib).
    iso2mesh_randseed : int, optional
        Random seed for color generation (used for loops).

    Returns
    -------
    hh : list
        Handles to plotted elements.
    """
    edges = np.asarray(edges, order="F")  # Flatten in F order if needed
    hh = []

    if edges.size == 0:
        return hh

    edlen = edges.shape[0]
    rng_state = np.random.get_state()

    if edges.ndim == 1 or edges.shape[1] == 1:
        # Loop: NaN-separated index list
        randseed = int("623F9A9E", 16)
        if "iso2mesh_randseed" in kwargs:
            randseed = kwargs["iso2mesh_randseed"]
        np.random.seed(randseed)

        loops = edges.flatten(order="F")
        if not np.isnan(loops[-1]):
            loops = np.append(loops, np.nan)

        seg = np.where(np.isnan(loops))[0]
        seghead = 0

        for i in seg:
            segment = loops[seghead:i]
            segment = segment.astype(int) - 1  # 1-based to 0-based
            if segment.size > 1:
                (h,) = plt.plot(
                    node[segment, 0],
                    node[segment, 1],
                    node[segment, 2] if node.shape[1] >= 3 else None,
                    color=np.random.rand(
                        3,
                    ),
                    *args,
                    **kwargs,
                )
                hh.append(h)
            seghead = i + 1
    else:
        from mpl_toolkits.mplot3d.art3d import Line3DCollection

        # Edge list: each row connects 2 nodes
        edges = edges.astype(int) - 1  # 1-based to 0-based

        if node.shape[1] >= 3:
            ax = plt.gca()

            if ax.name != "3d":
                plt.figure()  # Create a new figure
                ax = plt.gcf().add_subplot(
                    projection="3d"
                )  # Add 3D axes to the current figure

            segments = [[node[start], node[end]] for start, end in edges]
            h = Line3DCollection(segments, **kwargs)
            ax.add_collection3d(h)
            _autoscale_3d(ax, node)

            hh.append(h)
        else:
            x = node[:, 0].flatten()
            y = node[:, 1].flatten()
            h = plt.plot(x[edges.T], y[edges.T], *args, **kwargs)

        hh.append(h)

    np.random.set_state(rng_state)
    return hh


# _________________________________________________________________________________________________________


def plotmesh(node, *args, **kwargs):
    """
    plotmesh(node, face, elem, opt) → hm
    Plot surface and volumetric meshes in 3D.
    Converts 1-based MATLAB indices in `face` and `elem` to 0-based.
    Supports optional selector strings and stylistic options.
    """

    selector = None
    opt = []
    face = None
    elem = None

    # Parse inputs: detect selector strings, face/elem arrays, opts
    for i, a in enumerate(args):
        if isinstance(a, str):
            if any(c in a for c in "<>=&|") and any(c in a for c in "xyzXYZ"):
                selector = a
                opt = list(args[i + 1 :])
                break
            else:
                opt = list(args[i:])
                break
        else:
            if i == 0:
                if isinstance(a, list) or (
                    isinstance(a, np.ndarray) and a.ndim == 2 and a.shape[1] < 4
                ):
                    face = a
                elif isinstance(a, np.ndarray) and a.ndim == 2 and a.shape[1] in (4, 5):
                    uniq = np.unique(a[:, 3])
                    counts = np.bincount(a[:, 3].astype(int))
                    if len(uniq) == 1 or np.any(counts > 50):
                        face = a
                    else:
                        elem = a
                else:
                    elem = a
            elif i == 1:
                face = args[0]
                elem = a

    handles = []

    ax = kwargs.get("parent", None)

    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
    else:
        del kwargs["parent"]

    # Plot points if no face/elem
    if face is None and elem is None:
        x, y, z = node[:, 0], node[:, 1], node[:, 2]
        idx = (
            np.where(eval(selector, {"x": x, "y": y, "z": z}))[0]
            if selector
            else slice(None)
        )
        if getattr(idx, "size", None) == 0:
            print("Warning: nothing to plot")
            return None
        ax.plot(x[idx], y[idx], z[idx], *opt)
        _autoscale_3d(ax, node)
        plt.show(block=False)
        return ax

    # Plot surface mesh
    if face is not None:
        if isinstance(face, list):
            ax = plotsurf(node, face, opt, *args, **kwargs)
            handles.append(ax)
        else:
            c0 = meshcentroid(node[:, :3], face[:, :3])
            x, y, z = c0[:, 0], c0[:, 1], c0[:, 2]
            idx = (
                np.where(eval(selector, {"x": x, "y": y, "z": z}))[0]
                if selector
                else slice(None)
            )
            if getattr(idx, "size", None) == 0:
                print("Warning: nothing to plot")
                return None
            ax = plotsurf(node, face[idx, :], opt, *args, **kwargs)
            handles.append(ax)

    # Plot tetrahedral mesh
    if elem is not None:
        c0 = meshcentroid(node[:, :3], elem[:, :4])
        x, y, z = c0[:, 0], c0[:, 1], c0[:, 2]
        idx = (
            np.where(eval(selector, {"x": x, "y": y, "z": z}))[0]
            if selector
            else slice(None)
        )
        if getattr(idx, "size", None) == 0:
            print("Warning: nothing to plot")
            return None
        ax = plottetra(node, elem[idx, :], opt, *args, **kwargs)
        handles.append(ax)

    plt.show(block=False)
    return handles if len(handles) > 1 else handles[0]


def _get_face_triangles(node, face, selector):
    """Convert 1-based faces to triangles and apply selector filter."""
    face = np.asarray(face)
    face3 = face[:, :3].astype(int) - 1
    tris = node[face3, :3]
    if selector:
        cent = tris.mean(axis=1)
        idx = np.where(
            eval(selector, {"x": cent[:, 0], "y": cent[:, 1], "z": cent[:, 2]})
        )[0]
        tris = tris[idx]
    return tris


def _autoscale_3d(ax, points):
    x, y, z = points[:, 0], points[:, 1], points[:, 2]
    ax.set_xlim([x.min(), x.max()])
    ax.set_ylim([y.min(), y.max()])
    ax.set_zlim([z.min(), z.max()])
    boxas = [x.max() - x.min(), y.max() - y.min(), z.max() - z.min()]
    ax.set_box_aspect(boxas)


def _extract_poly_opts(opt):
    """Extract facecolor/edgecolor options for Poly3DCollection."""
    d = {}
    if "facecolor" in opt:
        d["facecolor"] = opt[opt.index("facecolor") + 1]
    else:
        d["facecolor"] = "white"
    if "edgecolor" in opt:
        d["edgecolor"] = opt[opt.index("edgecolor") + 1]
    else:
        d["edgecolor"] = "k"
    return d
