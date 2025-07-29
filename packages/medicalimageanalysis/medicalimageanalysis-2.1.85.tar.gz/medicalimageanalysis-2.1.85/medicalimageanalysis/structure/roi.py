"""
Morfeus lab
The University of Texas
MD Anderson Cancer Center
Author - Caleb O'Connor
Email - csoconnor@mdanderson.org

Description:

Structure:

"""

import vtk
import numpy as np
import SimpleITK as sitk

from scipy.spatial.transform import Rotation

from ..utils.mesh.surface import Refinement
from ..utils.conversion import ContourToDiscreteMesh


class Roi(object):
    def __init__(self, image, position=None, name=None, color=None, visible=False, filepaths=None, plane=None):
        self.image = image

        self.name = name
        self.visible = visible
        self.color = color
        self.filepaths = filepaths

        if plane is not None:
            self.plane = plane
        else:
            self.plane = self.image.plane

        if position is not None:
            self.contour_position = position
            self.contour_pixel = self.convert_position_to_pixel(position)
        else:
            self.contour_position = None
            self.contour_pixel = None

        self.mesh = None

        self.volume = None
        self.com = None
        self.bounds = None

        self.rotated_mesh = None
        self.multi_color = None

    def add_mesh(self, mesh):
        self.mesh = mesh

        self.volume = mesh.volume
        self.com = mesh.center
        self.bounds = mesh.bounds

    def clear(self):
        self.contour_position = None
        self.contour_pixel = None

        self.mesh = None
        self.volume = None
        self.com = None
        self.bounds = None

        self.multi_color = None

    def convert_position_to_pixel(self, position=None):
        if self.plane == 'Coronal':
            print(1)
        position_to_pixel_matrix = self.image.display.compute_matrix_position_to_pixel()

        pixel = []
        for ii, pos in enumerate(position):
            p_concat = np.concatenate((pos, np.ones((pos.shape[0], 1))), axis=1)
            pixel_3_axis = p_concat.dot(position_to_pixel_matrix.T)[:, :3]
            pixel += [np.vstack((pixel_3_axis, pixel_3_axis[0, :]))]

        return pixel

    def convert_pixel_to_position(self, pixel=None):
        pixel_to_position_matrix = self.image.display.compute_matrix_pixel_to_position(base=False)

        position = []
        for ii, pix in enumerate(pixel):
            p_concat = np.concatenate((pix, np.ones((pix.shape[0], 1))), axis=1)
            position += [p_concat.dot(pixel_to_position_matrix.T)[:, :3]]

        return position

    def create_mesh(self, smoothing_num_iterations=20, smoothing_relaxation_factor=.5, smoothing_constraint_distance=1):
        meshing = ContourToDiscreteMesh(contour_pixel=self.contour_pixel,
                                        spacing=self.image.spacing,
                                        origin=self.image.origin,
                                        dimensions=self.image.dimensions,
                                        matrix=self.image.matrix,
                                        plane=self.plane)
        self.mesh = meshing.compute_mesh(smoothing_num_iterations=smoothing_num_iterations,
                                         smoothing_relaxation_factor=smoothing_relaxation_factor,
                                         smoothing_constraint_distance=smoothing_constraint_distance)
        self.volume = self.mesh.volume
        self.com = self.mesh.center
        self.bounds = self.mesh.bounds

    def create_discrete_mesh(self):
        meshing = ContourToDiscreteMesh(contour_pixel=self.contour_pixel,
                                        spacing=self.image.spacing,
                                        origin=self.image.origin,
                                        dimensions=self.image.dimensions,
                                        matrix=self.image.matrix,
                                        plane=self.plane)
        self.mesh = meshing.compute_mesh(discrete=True)

        self.volume = self.mesh.volume
        self.com = self.mesh.center
        self.bounds = self.mesh.bounds

    def create_display_mesh(self, iterations=20, angle=60, passband=0.001):
        refine = Refinement(self.mesh)
        self.mesh = refine.smooth(iterations=iterations, angle=angle, passband=passband)

    def create_decimate_mesh(self, percent=None):
        if percent is None:
            points = np.round(10 * np.sqrt(self.mesh.number_of_points))
            percent = 1 - (points / self.mesh.number_of_points)

        return self.mesh.decimate(percent)

    def create_cluster_mesh(self, points=None):
        refine = Refinement(self.mesh)

        return refine.cluster(points=points)

    def compute_contour(self, slice_location):
        contour_list = []
        if self.contour_pixel is not None:
            if self.plane == 'Axial':
                roi_z = [np.round(c[0, 2]).astype(int) for c in self.contour_pixel]
                keep_idx = np.argwhere(np.asarray(roi_z) == slice_location)

                if len(keep_idx) > 0:
                    for ii, idx in enumerate(keep_idx):
                        contour_corrected = np.vstack((self.contour_pixel[idx[0]][:, 0:2],
                                                       self.contour_pixel[idx[0]][0, 0:2]))
                        contour_corrected[:, 1] = self.image.dimensions[1] - contour_corrected[:, 1]
                        contour_list += [contour_corrected]

            elif self.plane == 'Coronal':
                roi_y = [np.round(c[0, 1]).astype(int) for c in self.contour_pixel]
                keep_idx = np.argwhere(np.asarray(roi_y) == slice_location)

                if len(keep_idx) > 0:
                    for ii, idx in enumerate(keep_idx):
                        pixel_reshape = np.column_stack((self.contour_pixel[idx[0]][:, 0],
                                                         self.contour_pixel[idx[0]][:, 2]))
                        stack = np.asarray([self.contour_pixel[idx[0]][0, 0], self.contour_pixel[idx[0]][0, 2]])
                        contour_corrected = np.vstack((pixel_reshape, stack))
                        contour_list += [contour_corrected]

            else:
                roi_x = [np.round(c[0, 0]).astype(int) for c in self.contour_pixel]
                keep_idx = np.argwhere(np.asarray(roi_x) == slice_location)

                if len(keep_idx) > 0:
                    for ii, idx in enumerate(keep_idx):
                        contour_corrected = np.vstack((self.contour_pixel[idx[0]][:, 1:],
                                                       self.contour_pixel[idx[0]][0, 1:]))
                        contour_list += [contour_corrected]

        return contour_list

    def compute_mask(self):
        mask = ContourToDiscreteMesh(contour_pixel=self.contour_pixel,
                                     spacing=self.image.spacing,
                                     origin=self.image.origin,
                                     dimensions=self.image.dimensions,
                                     matrix=self.image.matrix,
                                     plane=self.plane)

        return mask.mask

    def compute_mesh_slice(self, location=None, slice_plane=None, return_pixel=False):
        matrix = self.image.display.matrix
        if slice_plane == 'Axial':
            normal = matrix[:3, 2]
        elif slice_plane == 'Coronal':
            normal = matrix[:3, 1]
        else:
            normal = matrix[:3, 0]

        roi_slice = self.mesh.slice(normal=normal, origin=location)

        if return_pixel:
            if roi_slice.number_of_points > 0:
                roi_strip = roi_slice.strip()
                position = [np.asarray(c.points) for c in roi_strip.cell]
                lines = roi_strip.lines

                if len(position) > 1:
                    position_correction = self.line_deconstruction(lines, position)

                else:
                    position_correction = position

                pixels = self.convert_position_to_pixel(position=position_correction)
                pixel_correct = self.pixel_slice_correction(pixels, slice_plane)

                return pixel_correct

            else:
                return []

        else:
            return roi_slice

    @staticmethod
    def line_deconstruction(lines, position):
        n = 0
        line_values = []
        for ii, p in enumerate(position):
            if ii == 0:
                n = len(p)
                line_splits = [1, len(p)]
            else:
                line_idx = n + 2
                n = line_idx + len(p) - 1
                line_splits = [line_idx, line_idx + len(p) - 1]
            line_values += [[lines[line_splits[0]], lines[line_splits[1]]]]

        line_values = np.vstack(line_values)

        order_idx = []
        m = 0
        while m >= 0:
            if line_values[m, 0] == line_values[m, 1]:
                order_idx += [[m]]

                combined_idx = np.sort(np.abs([item for sublist in order_idx for item in sublist]))
                mm = [ii for ii in range(line_values.shape[0]) if ii not in combined_idx]
                if len(mm) > 0:
                    m = mm[0]
                else:
                    m = -100

            else:
                hold_idx = [m]
                initial_value = line_values[m, 0]
                value = line_values[m, 1]
                n = 0
                while n >= 0:
                    check_1 = [idx for idx in np.where(line_values[:, 0] == value)[0] if idx != m and idx != n]
                    check_2 = [idx for idx in np.where(line_values[:, 1] == value)[0] if idx != m and idx != n]

                    if len(check_1) > 0:
                        hold_idx += [check_1[0]]
                        if line_values[check_1[0], 1] == initial_value:
                            order_idx += [hold_idx]
                            n = -100

                            combined_idx = np.sort(np.abs([item for sublist in order_idx for item in sublist]))
                            mm = [ii for ii in range(line_values.shape[0]) if ii not in combined_idx]
                            if len(mm) > 0:
                                m = mm[0]
                            else:
                                m = -100

                        else:
                            n = check_1[0]
                            value = line_values[n, 1]

                    elif len(check_2) > 0:
                        hold_idx += [-check_2[0]]
                        if line_values[check_2[0], 0] == initial_value:
                            order_idx += [hold_idx]
                            n = -100

                            combined_idx = np.sort(np.abs([item for sublist in order_idx for item in sublist]))
                            mm = [ii for ii in range(line_values.shape[0]) if ii not in combined_idx]
                            if len(mm) > 0:
                                m = mm[0]
                            else:
                                m = -100

                        else:
                            n = check_2[0]
                            value = line_values[n, 0]

                    else:
                        print('fail')
                        n = -100
                        m = -100

        position_correction = []
        for idx in order_idx:
            if isinstance(idx, int):
                position_correction += [position[idx]]

            else:
                position_hold = []
                for ii in idx:
                    if ii >= 0:
                        position_hold += [position[ii]]
                    else:
                        position_hold += [np.flip(position[np.abs(ii)], axis=0)]

                position_correction += [np.vstack(position_hold)]

        return position_correction

    def pixel_slice_correction(self, pixels, plane):
        pixel_corrected = []
        for pixel in pixels:

            if plane in 'Axial':
                pixel_reshape = pixel[:, :2]
                pixel_corrected += [np.asarray([pixel_reshape[:, 0],
                                                self.image.dimensions[1] - pixel_reshape[:, 1]]).T]

            elif plane == 'Coronal':
                pixel_reshape = np.column_stack((pixel[:, 0], pixel[:, 2]))
                pixel_corrected += [pixel_reshape]

            else:
                pixel_reshape = pixel[:, 1:]
                pixel_corrected += [pixel_reshape]

        return pixel_corrected

    def update_pixel(self, pixel, plane='Axial'):
        self.plane = plane
        self.contour_pixel = pixel
        self.contour_position = self.convert_pixel_to_position(pixel=pixel)
        self.create_mesh()
