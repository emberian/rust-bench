# `rust-bench`

This repo contains scripts and programs that were onced used in the (now
defunct) "Is Rust Slim Yet?" website. It has the ability to use Linux cgroups
to monitor memory usage in a very fine-grained manner and plot the resulting
data.

As these scripts were only ever used by me, you may need to frob some paths
here and there in the source.

# `auto-bench.py`

This is a wrapper script that takes installed rust build trees in
`/mnt/rustb` and runs `benchit.py` on all the ones that don't yet have
benchmarking data in `/home/cmr/benches/data`. It will also force benchmarking
for those commits listed in `/home/cmr/benches/bench-override.txt`, and do
those first.

# `auto-build.py`

This is no longer used, it was replaced with the pure-Rust
[multibuilder](https://github.com/huonw/multibuilder). It does pretty much the
same thing but worse.

# `benchit-build.py`

This was a script that I had multibuilder invoke to build a commit.

# `benchit.py`

This script does the meat of the benchmarking, by invoking `mem-bench` on each
`rustc` build and such. It has a lot of logic that knows how to build Rust
properly all the way back to 0.5.

# `plot-twoprogs.R`

A little R script for plotting a comparative graph of the memory usage of two
runs of rustc from the JSON that `mem-bench` outputs. Invoke like
`R plot-twoprogs.R graph.png baseline-title under-test-title baseline.json
under-test.json`.

I stopped using this in favor of...

# `plot_data.py`

Same as `plot-twoprogs.R`, pretty much, but in Python and a bit fancier.
Invoked pretty much the same way, see `plot_data.py --help`.

# `plot_one.py`

Similar to `plot_data.py` but plots only one memory use graph, instead of
comparing two programs.

# `setup.py`

This is a Python package! This has the metadata for installing with a Python
package manager.

# `mem-bench`

This is the Rust portion of this repo, in `src` and built with Cargo. It will
do the memory-use polling and serialization. I used to do this in pure Python
but gosh was it slow. It also had a bad habit of using all of the memory
on my system, and imposed a noticable time hit on the program being
measured.

# License

All code here is available to you under the BSL-1.0, MIT, or ASL-2.0 licenses
at your choice.
