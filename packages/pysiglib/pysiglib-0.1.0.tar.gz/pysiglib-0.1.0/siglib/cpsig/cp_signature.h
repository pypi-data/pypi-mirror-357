/* Copyright 2025 Daniil Shmelev
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ========================================================================= */

#pragma once
#include "cppch.h"

#include "multithreading.h"
#include "cp_tensor_poly.h"

#include "cp_path.h"
#include "macros.h"
#ifdef VEC
#include "cp_vector_funcs.h"
#endif


template<typename T>
FORCE_INLINE void linear_signature_(Point<T>& start_pt, Point<T>& end_pt, double* out, uint64_t dimension, uint64_t degree, uint64_t* level_index)
{
	//Computes the signature of a linear segment joining start_pt and end_pt
	out[0] = 1.;

	for (uint64_t i = 0UL; i < dimension; ++i)
		out[i + 1] = static_cast<double>(end_pt[i] - start_pt[i]);
	
	double one_over_level;
	double left_over_level;

	for (uint64_t level = 2UL; level <= degree; ++level) {
		one_over_level = 1. / static_cast<double>(level);
		double* result_ptr = out + level_index[level];
		const double* left_ptr_upper_bound = out + level_index[level];

		for (double* left_ptr = out + level_index[level - 1]; left_ptr != left_ptr_upper_bound; ++left_ptr) {
			left_over_level = (*left_ptr) * one_over_level;
			for (double* right_ptr = out + 1; right_ptr != out + dimension + 1; ++right_ptr) {
				*(result_ptr++) = left_over_level * (*right_ptr);
			}
		}
	}
}

template<typename T>
void signature_naive_(Path<T>& path, double* out, uint64_t degree)
{
	const uint64_t dimension = path.dimension();

	Point<T> prev_pt(path.begin());
	Point<T> next_pt(path.begin());
	++next_pt;

	auto level_index_uptr = std::make_unique<uint64_t[]>(degree + 2);
	uint64_t* level_index = level_index_uptr.get();

	level_index[0] = 0UL;
	for (uint64_t i = 1UL; i <= degree + 1UL; i++)
		level_index[i] = level_index[i - 1UL] * dimension + 1;

	linear_signature_(prev_pt, next_pt, out, dimension, degree, level_index); //Zeroth step

	if (path.length() == 2UL) { return; }

	++prev_pt;
	++next_pt;

	auto linear_signature_uptr = std::make_unique<double[]>(::sig_length(dimension, degree));
	double* linear_signature = linear_signature_uptr.get();

	Point<T> last_pt(path.end());

	for (; next_pt != last_pt; ++prev_pt, ++next_pt) {

		linear_signature_(prev_pt, next_pt, linear_signature, dimension, degree, level_index);

		sig_combine_inplace_(out, linear_signature, degree, level_index);
	}
}

template<typename T>
void signature_horner_(Path<T>& path, double* out, uint64_t degree)
{
	const uint64_t dimension = path.dimension();

	Point<T> prev_pt = path.begin();
	Point<T> next_pt = path.begin();
	++next_pt;

	auto level_index_uptr = std::make_unique<uint64_t[]>(degree + 2);
	uint64_t* level_index = level_index_uptr.get();

	level_index[0] = 0UL;
	for (uint64_t i = 1UL; i <= degree + 1UL; i++)
		level_index[i] = level_index[i - 1UL] * dimension + 1UL;

	linear_signature_(prev_pt, next_pt, out, dimension, degree, level_index); //Zeroth step

	if (path.length() == 2UL) { return; }

	++prev_pt;
	++next_pt;
	
	auto horner_step_uptr = std::make_unique<double[]>(level_index[degree + 1UL] - level_index[degree]);
	double* horner_step = horner_step_uptr.get();

	auto increments_uptr = std::make_unique<double[]>(dimension);
	double* increments = increments_uptr.get();

	Point<T> last_pt(path.end());

	for (; next_pt != last_pt; ++prev_pt, ++next_pt) {
		for (uint64_t i = 0UL; i < dimension; ++i)
			increments[i] = static_cast<double>(next_pt[i] - prev_pt[i]);

		for (int64_t target_level = static_cast<int64_t>(degree); target_level > 1L; --target_level) {

			double one_over_level = 1. / static_cast<double>(target_level);

			//left_level = 0
			//assign z / target_level to horner_step
			for (uint64_t i = 0UL; i < dimension; ++i)
				horner_step[i] = increments[i] * one_over_level;

			for (int64_t left_level = 1L, right_level = target_level - 1L;
				left_level < target_level - 1L; 
				++left_level, --right_level) { //for each, add current left_level and times by z / right_level

				const uint64_t left_level_size = level_index[left_level + 1UL] - level_index[left_level];
				one_over_level = 1. / static_cast<double>(right_level);

				//Horner stuff
				//Add
				double* left_ptr_1 = out + level_index[left_level];
				for (uint64_t i = 0UL; i < left_level_size; ++i) {
					horner_step[i] += *(left_ptr_1++);
				}

				//Multiply
#ifdef VEC
				double left_over_level;
				double* result_ptr = horner_step + level_index[left_level + 2UL] - level_index[left_level + 1UL] - dimension;
				for (double* left_ptr = horner_step + left_level_size - 1UL; left_ptr != horner_step - 1UL; --left_ptr, result_ptr -= dimension) {
					left_over_level = (*left_ptr) * one_over_level;
					vec_mult_assign(result_ptr, increments, left_over_level, dimension);
				}
#else
				double left_over_level;
				double* result_ptr = horner_step + level_index[left_level + 2UL] - level_index[left_level + 1UL];
				for (double* left_ptr = horner_step + left_level_size - 1UL; left_ptr != horner_step - 1UL; --left_ptr) {
					left_over_level = (*left_ptr) * one_over_level;
					for (double* right_ptr = increments + dimension - 1UL; right_ptr != increments - 1UL; --right_ptr) {
						*(--result_ptr) = left_over_level * (*right_ptr);
					}
				}
#endif
			}

			//======================= Do last iteration (left_level = target_level - 1) separately for speed, and add result straight into out

			const uint64_t left_level_size = level_index[target_level] - level_index[target_level - 1UL];

			//Horner stuff
			//Add
			double* left_ptr_1 = out + level_index[target_level - 1UL];
			for (uint64_t i = 0UL; i < left_level_size; ++i) {
				horner_step[i] += *(left_ptr_1++);
			}

			//Multiply and add, writing straight into out
#ifdef VEC
			double* result_ptr = out + level_index[target_level + 1] - dimension;
			for (double* left_ptr = horner_step + left_level_size - 1UL; left_ptr != horner_step - 1UL; --left_ptr, result_ptr -= dimension) {
				vec_mult_add(result_ptr, increments, *left_ptr, dimension);
			}
#else
			double* result_ptr = out + level_index[target_level + 1];
			for (double* left_ptr = horner_step + left_level_size - 1UL; left_ptr != horner_step - 1UL; --left_ptr) {
				for (double* right_ptr = increments + dimension - 1UL; right_ptr != increments - 1UL; --right_ptr) {
					*(--result_ptr) += (*left_ptr) * (*right_ptr); //no one_over_level here, as right_level = 1
				}
			}
#endif
		}
		//Update target_level == 1
		for (uint64_t i = 0; i < dimension; ++i)
			out[i + 1] += increments[i];
	}
}

template<typename T>
void signature_(T* path, double* out, uint64_t dimension, uint64_t length, uint64_t degree, bool time_aug = false, bool lead_lag = false, bool horner = true)
{
	if (dimension == 0) { throw std::invalid_argument("signature received path of dimension 0"); }

	Path<T> path_obj(path, dimension, length, time_aug, lead_lag); //Work with path_obj to capture time_aug, lead_lag transformations

	if (path_obj.length() <= 1) {
		out[0] = 1.;
		uint64_t result_length = ::sig_length(path_obj.dimension(), degree);
		std::fill(out + 1, out + result_length, 0.);
		return;
	}
	if (degree == 0) { out[0] = 1.; return; }
	if (degree == 1) {
		Point<T> first_pt = path_obj.begin();
		Point<T> last_pt = --path_obj.end();
		out[0] = 1.;
		uint64_t dimension_ = path_obj.dimension();
		for (uint64_t i = 0; i < dimension_; ++i)
			out[i + 1] = static_cast<double>(last_pt[i] - first_pt[i]);
		return; 
	}

	if (horner)
		signature_horner_(path_obj, out, degree);
	else
		signature_naive_(path_obj, out, degree);
}

template<typename T>
void batch_signature_(T* path, double* out, uint64_t batch_size, uint64_t dimension, uint64_t length, uint64_t degree, bool time_aug = false, bool lead_lag = false, bool horner = true, int n_jobs = 1)
{
	//Deal with trivial cases
	if (dimension == 0) { throw std::invalid_argument("signature received path of dimension 0"); }

	Path<T> dummy_path_obj(nullptr, dimension, length, time_aug, lead_lag); //Work with path_obj to capture time_aug, lead_lag transformations

	const uint64_t result_length = ::sig_length(dummy_path_obj.dimension(), degree);

	if (dummy_path_obj.length() <= 1) {
		double* const out_end = out + result_length * batch_size;
		std::fill(out, out_end, 0.);
		for (double* out_ptr = out;
			out_ptr < out_end;
			out_ptr += result_length) {
			out_ptr[0] = 1.;
		}
		return;
	}
	if (degree == 0) { 
		std::fill(out, out + batch_size, 1.);
		return; }

	//General case and degree = 1 case
	const uint64_t flat_path_length = dimension * length;
	T* const data_end = path + flat_path_length * batch_size;

	std::function<void(T*, double*)> sig_func;

	if (degree == 1) {
		sig_func = [&](T* path_ptr, double* out_ptr) {
			Path<T> path_obj(path_ptr, dimension, length, time_aug, lead_lag);
			Point<T> first_pt = path_obj.begin();
			Point<T> last_pt = --path_obj.end();
			out_ptr[0] = 1.;
			for (uint64_t i = 0; i < path_obj.dimension(); ++i)
				out_ptr[i + 1] = static_cast<double>(last_pt[i] - first_pt[i]);
			};
	}
	else {
		if (horner) {
			sig_func = [&](T* path_ptr, double* out_ptr) {
				Path<T> path_obj(path_ptr, dimension, length, time_aug, lead_lag);
				signature_horner_<T>(path_obj, out_ptr, degree);
				};
		}
		else {
			sig_func = [&](T* path_ptr, double* out_ptr) {
				Path<T> path_obj(path_ptr, dimension, length, time_aug, lead_lag);
				signature_naive_<T>(path_obj, out_ptr, degree);
				};
		}
	}

	T* path_ptr;
	double* out_ptr;

	if (n_jobs != 1) {
		multi_threaded_batch(sig_func, path, out, batch_size, flat_path_length, result_length, n_jobs);
	}
	else {
		for (path_ptr = path, out_ptr = out;
			path_ptr < data_end;
			path_ptr += flat_path_length, out_ptr += result_length) {

			sig_func(path_ptr, out_ptr);
		}
	}
	return;
}