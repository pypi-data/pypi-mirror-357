use itertools::Itertools;
use ndarray::{Array2, ArrayView2, Axis};
use serde::{Deserialize, Serialize};

use super::Var;
use crate::{Result, ScalibError};

/// Selection of a subset of points in a trace: allows to map source traces to reduced traces that
/// are subsets of the original traces, keeping only th POIs.
/// Sorting constraints:
/// 1. For efficient scatter_pairs: pois of the same var tend to be consecutive in new2old.
/// 2. For predict_proba: values in new_poi_vars must be sorted.
/// 3. Can make a new POI map with subset of variables preserving 2. but not necessarily 1., and
///    without changing the order of POIs of each var. We can implement this by keeping new2old in
///    order, but dropping elements that are not needed anymore, and adapting values of new_poi_vars.
/// TODO:
/// - check construction of new2old + sort POIs before putting them in new2old (for
/// efficiency - need to compose shuffling of POIs)
/// - completely rewrite the algorithm for select_var.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PoiMap {
    /// List of POIs kept from the original traces.
    new2old: Vec<u32>,
    /// For each variable of interest, list of its POIs in the reduced traces.
    // TODO: have indices be i16 when possible.
    pub new_poi_vars: Vec<Vec<u32>>,
    // For each variable, the argsort of the vector of POIs.
    // (Used in reshuffling in original order means and scatter when they are genereated for
    // external inspection.)
    pub new_poi_var_shuffles: Vec<Vec<u32>>,
}

impl PoiMap {
    /// Crate a new PoiMap
    /// - `ns`: Source trace length
    /// - `poi_vars`: For each variable, the list of its POIs.
    pub fn new(ns: usize, poi_vars: &[Vec<u32>]) -> Result<Self> {
        let mut new2old = Vec::new();
        let mut old2new: Vec<Option<u32>> = vec![None; ns as usize];
        let mut new_poi_vars = Vec::new();
        let mut new_poi_var_shuffles = Vec::new();
        for pois in poi_vars {
            let shuffle = crate::utils::argsort(pois);
            let mut new_poi_var = shuffle
                .iter()
                .map(|poi_idx| -> Result<u32> {
                    let poi = pois[*poi_idx];
                    let new_poi = old2new
                        .get_mut(poi as usize)
                        .ok_or(ScalibError::PoiOutOfBound)?;
                    Ok(if let Some(new_poi) = new_poi {
                        *new_poi
                    } else {
                        let n_pois = new2old.len() as u32;
                        *new_poi = Some(n_pois);
                        new2old.push(poi);
                        n_pois
                    })
                })
                .collect::<Result<Vec<_>>>()?;
            let shuffle2 = crate::utils::argsort(&new_poi_var);
            let new_poi_var_shuffle = shuffle2
                .iter()
                .map(|x| shuffle[*x].try_into().unwrap())
                .collect::<Vec<_>>();
            new_poi_var.sort_unstable();
            new_poi_vars.push(new_poi_var);
            new_poi_var_shuffles.push(new_poi_var_shuffle);
        }
        Ok(Self {
            new2old,
            new_poi_vars,
            new_poi_var_shuffles,
        })
    }
    /// Length of the reduced traces.
    pub fn len(&self) -> usize {
        self.new2old.len()
    }
    /// Merged list of POI indices (it is sorted).
    pub fn kept_indices(&self) -> &[u32] {
        self.new2old.as_slice()
    }
    /// POIs for the given var in the reduced traces
    pub fn new_pois(&self, var: Var) -> &[u32] {
        &self.new_poi_vars[var as usize]
    }
    /// POIs for all vars in the reduced traces
    pub fn new_pois_vars(&self) -> &[Vec<u32>] {
        &self.new_poi_vars
    }
    /// Number of POIs for a given var.
    pub fn n_pois(&self, var: Var) -> usize {
        self.new_pois(var).len()
    }
    /// POI blocks for MultiLda.predict_proba
    pub fn poi_blocks(&self) -> Vec<Vec<(std::ops::Range<usize>, Vec<u16>)>> {
        use super::POI_BLOCK_SIZE;
        assert!(POI_BLOCK_SIZE < (u16::MAX as usize));
        let n_poi_blocks = self.len().div_ceil(POI_BLOCK_SIZE);
        self.new_pois_vars()
            .iter()
            .map(|pois| {
                let mut res = vec![(0..0, vec![]); n_poi_blocks];
                for poi in pois.iter() {
                    let poi = *poi as usize;
                    res[poi / POI_BLOCK_SIZE]
                        .1
                        .push((poi % POI_BLOCK_SIZE) as u16);
                }
                let mut npois = 0;
                for (r, pois) in res.iter_mut() {
                    let new_npois = npois + pois.len();
                    *r = npois..new_npois;
                    npois = new_npois;
                }
                res
            })
            .collect()
    }
    /// Create a new PoiMap with only a subset of the variables.
    pub fn select_vars(&self, vars: &[super::Var]) -> Result<Self> {
        let mut kept_vars = vec![false; self.new2old.len()];
        for var in vars {
            for poi in &self.new_poi_vars[*var as usize] {
                kept_vars[*poi as usize] = true;
            }
        }
        let mut count_kept = 0;
        let oldnew2new = (0..self.new2old.len())
            .map(|i| {
                kept_vars[i].then(|| {
                    count_kept += 1;
                    count_kept - 1
                })
            })
            .collect::<Vec<_>>();
        let new2old = kept_vars
            .iter()
            .positions(|x| *x)
            .map(|x| self.new2old[x])
            .collect_vec();
        let new_poi_vars = vars
            .iter()
            .map(|var| {
                let pois = &self.new_poi_vars[*var as usize];
                pois.iter()
                    .map(|poi| oldnew2new[*poi as usize].unwrap())
                    .collect_vec()
            })
            .collect_vec();
        let new_poi_var_shuffles = vars
            .iter()
            .map(|var| self.new_poi_var_shuffles[*var as usize].clone())
            .collect_vec();
        let res = Self {
            new2old,
            new_poi_vars,
            new_poi_var_shuffles,
        };
        debug_assert!(vars.iter().enumerate().all(|(i, v)| itertools::equal(
            self.new_pois(*v).iter().map(|p| self.new2old[*p as usize]),
            res.new_pois(i as Var)
                .iter()
                .map(|p| res.new2old[*p as usize])
        )));
        Ok(res)
    }
    /// All pairs `(i, j)` such that `i` and `j` are POIs of the same var in the reduced traces,
    /// and `i <= j`.
    pub fn mapped_pairs(&self, var: Var) -> impl Iterator<Item = (u32, u32)> + '_ {
        let pois = self.new_pois(var);
        super::MultiLdaAcc::pairs_n(pois.len() as u32)
            .map(|(i, j)| (pois[i as usize], pois[j as usize]))
    }
    /// Return a "batched" representation that takes chunks of N traces, then each poi is an array
    /// of N values. Overall, the result is an Array2<[i16; N]> with shape (ceil(ntraces/N),
    /// npois).
    // TODO: make a parallel version of this.
    #[inline(never)]
    pub fn select_batches<const N: usize>(&self, traces: ArrayView2<i16>) -> Array2<AA<N>> {
        let n_batches = traces.shape()[0].div_ceil(N);
        let mut res = Array2::from_elem((n_batches, self.len()), AA([0; N]));
        let chunk_iter = traces.axis_chunks_iter(Axis(0), N);
        for (chunk, mut batch) in chunk_iter.zip(res.outer_iter_mut()) {
            transpose_big(chunk, batch.as_slice_mut().unwrap(), self.kept_indices());
        }
        res
    }

    #[inline(never)]
    pub fn select_transpose(&self, traces: ArrayView2<i16>) -> Array2<i16> {
        Array2::from_shape_fn((self.len(), traces.shape()[0]), |(poi_i, ti)| {
            traces[(ti, self.new2old[poi_i] as usize)]
        })
    }
}

/// Wrapper to ensure good alignment w.r.t. SIMD instructions.
#[derive(Debug, Clone)]
#[repr(C, align(32))]
pub struct AA<const N: usize>(pub [i16; N]);

/// Copy columns the columns of `chunk` indexed by `kept_indices` into elements of `batch`.
/// If the height of `chunk` is less than `N`, then write `0` in the remaining elements.
/// Then length of `batch` and the length of `kept_indices` must match.
#[inline(never)]
fn transpose_big<const N: usize>(
    chunk: ArrayView2<i16>,
    batch: &mut [AA<N>],
    kept_indices: &[u32],
) {
    assert!(chunk.shape()[0] <= N);
    assert_eq!(batch.len(), kept_indices.len());
    if chunk.shape()[0] != N {
        batch.fill(AA([0; N]));
    }
    const SUB_CHUNK_M: usize = 8;
    const SUB_CHUNK_N: usize = 8;
    for (sb_i, traces_sb) in chunk.axis_chunks_iter(Axis(0), SUB_CHUNK_M).enumerate() {
        for (indices_sb, chunk_sb) in kept_indices
            .chunks(SUB_CHUNK_N)
            .zip(batch.chunks_mut(SUB_CHUNK_N))
        {
            if indices_sb.len() == SUB_CHUNK_N && traces_sb.shape()[0] == SUB_CHUNK_M {
                let mut chunk_sb_iter = chunk_sb.iter_mut();
                let y: [&mut [i16; SUB_CHUNK_M]; SUB_CHUNK_N] = std::array::from_fn(|_| {
                    let offset = sb_i * SUB_CHUNK_M;
                    let sl = &mut chunk_sb_iter.next().unwrap().0[offset..(offset + SUB_CHUNK_M)];
                    sl.try_into().unwrap()
                });
                transpose_small(traces_sb, indices_sb, y);
            } else {
                for (idx, batch_item) in indices_sb.iter().zip(chunk_sb.iter_mut()) {
                    for i in 0..traces_sb.shape()[0] {
                        batch_item.0[sb_i * SUB_CHUNK_M + i] = traces_sb[(i, *idx as usize)];
                    }
                }
            }
        }
    }
}

/// For each of the N indices and element of y, copy the column of x with the index into y.
// TODO: maybe there can be a bit of SIMD opt here...
// basic: load i16 and insert in SIMD, write-back as full word.
// improved: detect when indices are consecutive, and go more SIMD there (maybe 64-bit is enough ?)
// https://stackoverflow.com/questions/2517584/transpose-for-8-registers-of-16-bit-elements-on-sse2-ssse3/2518670#2518670
#[inline(never)]
fn transpose_small<const M: usize, const N: usize>(
    x: ArrayView2<i16>,
    indices: &[u32],
    y: [&mut [i16; M]; N],
) {
    assert_eq!(x.shape()[0], M);
    assert_eq!(indices.len(), N);
    for j in 0..N {
        for i in 0..M {
            y[j][i] = x[(i, indices[j] as usize)];
        }
    }
}
