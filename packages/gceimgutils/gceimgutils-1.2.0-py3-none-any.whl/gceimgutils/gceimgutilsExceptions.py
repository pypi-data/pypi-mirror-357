# Copyright (c) 2021 SUSE LLC
#
# This file is part of gceimgutils.
#
# gceimgutils is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gceimgutils is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gceimgutils.  If not, see <http://www.gnu.org/licenses/>.


class GCEImgUtilsException(Exception):
    pass


class GCEProjectCredentialsException(GCEImgUtilsException):
    pass


class GCERemoveImgException(GCEImgUtilsException):
    pass


class GCEListImgException(GCEImgUtilsException):
    pass


class GCEDeprecateImgException(GCEImgUtilsException):
    pass


class GCECreateImgException(GCEImgUtilsException):
    pass


class GCERemoveBlobException(GCEImgUtilsException):
    pass


class GCEUploadBlobException(GCEImgUtilsException):
    pass
