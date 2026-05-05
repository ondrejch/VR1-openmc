#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
from pathlib import Path
import tempfile
import numpy as np
import openmc


# How to run
# plot_model.py -g geometry.xml -m materials.xml -o file_location/file.py --outdir plots --basis xy xz yz --pixels 1200 1200
# python ../../post_processing_plotting/plot_model.py -m materials.xml -g geometry.xml -o 2D_slice --basis xy --pixels 1000 1000 --width 400 400
#python plot_model.py -g ../offset_data/run_full_source_flat_centered/geometry.xml -m ../offset_data/run_full_source_flat_centered/materials.xml -o centered_plot --outdir plots --voxel --voxel-pixels 500 500 100 --vtk

def safe_center(lo, hi, fallback=0.0):
    lo = float(lo); hi = float(hi)
    if np.isfinite(lo) and np.isfinite(hi):
        return 0.5 * (lo + hi)
    return float(fallback)

def safe_extent(lo, hi, fallback=100.0):
    lo = float(lo); hi = float(hi)
    w = hi - lo
    if np.isfinite(lo) and np.isfinite(hi) and np.isfinite(w) and w > 0.0:
        return float(w)
    return float(fallback)

def choose_origin_and_width(basis, bb, origin_opt=None, width_opt=None, default_w=100.0):
    (xmin, ymin, zmin), (xmax, ymax, zmax) = bb
    cx = safe_center(xmin, xmax, 0.0)
    cy = safe_center(ymin, ymax, 0.0)
    cz = safe_center(zmin, zmax, 0.0)

    if origin_opt is None:
        origin = (cx, cy, cz)
    else:
        if len(origin_opt) != 3:
            raise ValueError("--origin must have exactly 3 numbers (x y z)")
        origin = tuple(float(v) for v in origin_opt)

    if width_opt is None:
        if basis == "xy":
            w1 = safe_extent(xmin, xmax, default_w)
            w2 = safe_extent(ymin, ymax, default_w)
        elif basis == "xz":
            w1 = safe_extent(xmin, xmax, default_w)
            w2 = safe_extent(zmin, zmax, default_w)
        elif basis == "yz":
            w1 = safe_extent(ymin, ymax, default_w)
            w2 = safe_extent(zmin, zmax, default_w)
        else:
            raise ValueError(f"unknown basis {basis}")
        width = (w1, w2)
    else:
        if len(width_opt) != 2:
            raise ValueError("--width must have exactly 2 numbers")
        width = tuple(float(v) for v in width_opt)

    return origin, width

def choose_origin_and_width_3d(bb, origin_opt=None, width_opt=None, default_w=100.0):
    """3D origin/width chooser for voxel plot."""
    (xmin, ymin, zmin), (xmax, ymax, zmax) = bb
    if origin_opt is None:
        origin = (
            safe_center(xmin, xmax, 0.0),
            safe_center(ymin, ymax, 0.0),
            safe_center(zmin, zmax, 0.0),
        )
    else:
        if len(origin_opt) != 3:
            raise ValueError("--voxel-origin must have exactly 3 numbers (x y z)")
        origin = tuple(float(v) for v in origin_opt)

    if width_opt is None:
        width = (
            safe_extent(xmin, xmax, default_w),
            safe_extent(ymin, ymax, default_w),
            safe_extent(zmin, zmax, default_w),
        )
    else:
        if len(width_opt) != 3:
            raise ValueError("--voxel-width must have exactly 3 numbers (wx wy wz)")
        width = tuple(float(v) for v in width_opt)

    return origin, width

def make_plot(basis, width, origin, pixels, color_by="material", filename=None):
    p = openmc.Plot()
    p.basis = basis
    p.width = width
    p.origin = origin
    p.pixels = pixels
    p.color_by = color_by  # 'material' or 'cell'
    if filename:
        p.filename = Path(filename).with_suffix('').name
    return p

def make_voxel_plot(width3, origin3, pixels3, color_by="material", filename=None):
    """3D voxel plot (writes HDF5 voxel file)."""
    p = openmc.Plot()
    p.type = 'voxel'               # 3D voxel plot
    p.width = tuple(width3)        # (wx, wy, wz)
    p.origin = tuple(origin3)      # (x, y, z)
    p.pixels = tuple(pixels3)      # (nx, ny, nz)
    p.color_by = color_by          # 'material' or 'cell' (controls stored IDs)
    if filename:
        p.filename = Path(filename).with_suffix('').name
    return p

def run_plotter_in_dir(workdir: Path):
    """Run the OpenMC plotter in workdir which must contain geometry.xml, materials.xml, plots.xml."""
    cwd0 = Path.cwd()
    try:
        os.chdir(workdir)
        if hasattr(openmc, "plot_geometry"):
            openmc.plot_geometry()
        else:
            subprocess.run(["openmc", "--plot"], check=True)
    finally:
        os.chdir(cwd0)

def main():
    ap = argparse.ArgumentParser(description="Plot 2D views and optional 3D voxel from OpenMC geometry/material XMLs.")
    ap.add_argument("-g", "--geometry", required=True, help="Path to geometry.xml")
    ap.add_argument("-m", "--materials", required=True, help="Path to materials.xml")
    ap.add_argument("-o", "--outdir", default="plots", help="Output directory for PNGs/voxel/VTK")
    ap.add_argument("--basis", nargs="+", default=["xy", "xz", "yz"],
                    choices=["xy", "xz", "yz"], help="One or more bases to plot")
    ap.add_argument("--pixels", nargs=2, type=int, default=[1200, 1200],
                    help="Image resolution (nx ny) for 2D slices, default 1200 1200")
    ap.add_argument("--width", nargs=2, type=float, default=None,
                    help="Override 2D width in the plot plane (w1 w2); default uses extents or 100 if unbounded")
    ap.add_argument("--origin", nargs=3, type=float, default=None,
                    help="Override origin for 2D plots (x y z); default centers finite axes and uses 0 on unbounded axes")
    ap.add_argument("--color-by", choices=["material", "cell"], default="material",
                    help="Color/ID by material or cell (applies to 2D colors and voxel IDs)")

    # --- 3D voxel options ---
    ap.add_argument("--voxel", action="store_true",
                    help="Generate a 3D voxel plot (HDF5) of the geometry")
    ap.add_argument("--voxel-pixels", nargs=3, type=int, default=[150, 150, 150],
                    help="Voxel resolution (nx ny nz), default 150 150 150")
    ap.add_argument("--voxel-width", nargs=3, type=float, default=None,
                    help="Voxel physical width (wx wy wz); default uses extents or 100 if unbounded")
    ap.add_argument("--voxel-origin", nargs=3, type=float, default=None,
                    help="Override voxel origin (x y z); default centers finite axes and uses 0 on unbounded axes")
    ap.add_argument("--voxel-name", default="voxel",
                    help="Base filename for the voxel file (no extension), default 'voxel'")
    ap.add_argument("--vtk", action="store_true",
                    help="Also convert voxel HDF5 to VTK .vti for VisIt/ParaView")

    args = ap.parse_args()

    geom_xml = Path(args.geometry).resolve()
    mats_xml = Path(args.materials).resolve()
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    # Load materials explicitly so Geometry.from_xml doesn't guess materials.xml path
    mats = openmc.Materials.from_xml(str(mats_xml))
    geom = openmc.Geometry.from_xml(str(geom_xml), materials=mats)

    # Get bounding box (can be ±inf on unbounded axes)
    try:
        bb = geom.bounding_box  # ((xmin,ymin,zmin),(xmax,ymax,zmax))
    except Exception:
        bb = ((-np.inf, -np.inf, -np.inf), (np.inf, np.inf, np.inf))

    plots = []
    # 2D slices
    for b in args.basis:
        origin2, width2 = choose_origin_and_width(b, bb, args.origin, args.width, default_w=100.0)
        print(f"[plot {b}] origin={origin2} width={width2} pixels={tuple(args.pixels)} color_by={args.color_by}")
        plots.append(make_plot(b, width2, origin2, tuple(args.pixels),
                               color_by=args.color_by, filename=f"plot_{b}"))

    # 3D voxel
    if args.voxel:
        vox_origin, vox_width = choose_origin_and_width_3d(bb, args.voxel_origin, args.voxel_width, default_w=100.0)
        print(f"[voxel] origin={vox_origin} width={vox_width} pixels={tuple(args.voxel_pixels)} color_by={args.color_by}")
        plots.append(make_voxel_plot(vox_width, vox_origin, tuple(args.voxel_pixels),
                                     color_by=args.color_by, filename=args.voxel_name))

    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        # Put expected filenames in the working dir for plotter
        shutil.copy2(geom_xml, tdir / "geometry.xml")
        shutil.copy2(mats_xml, tdir / "materials.xml")

        # Write plots.xml inside the temp dir
        cwd0 = Path.cwd()
        os.chdir(tdir)
        try:
            openmc.Plots(plots).export_to_xml()
        finally:
            os.chdir(cwd0)

        # Run plotter
        run_plotter_in_dir(tdir)

        # Copy PNGs back
        for png in sorted(tdir.glob("*.png")):
            shutil.copy2(png, outdir / png.name)

        # Copy voxel HDF5 and optionally convert to VTK
        if args.voxel:
            # Handle numbered outputs if multiple voxel plots are ever added
            voxel_h5s = sorted(tdir.glob(f"{Path(args.voxel_name).stem}*.h5"))
            if not voxel_h5s:
                # Fallback to any voxel*.h5
                voxel_h5s = sorted(tdir.glob("voxel*.h5"))

            for vf in voxel_h5s:
                out_h5 = outdir / vf.name
                shutil.copy2(vf, out_h5)
                print(f"Saved voxel file: {out_h5}")
                if args.vtk:
                    vti_path = outdir / (out_h5.stem + ".vti")
                    openmc.voxel_to_vtk(str(out_h5), output=str(vti_path))
                    print(f"Converted to VTK: {vti_path}")

    print(f"Saved 2D plots to: {outdir}")

if __name__ == "__main__":
    main()

