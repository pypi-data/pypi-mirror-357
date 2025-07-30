# Changelog
All notable changes to this project will be documented in this file.

## [0.0.32] - 2023-06-26

### Fixed
- Fixed structs in cells

## [0.0.23] - 2020-05-19

### Fixed

- Fix case in which a string contained in a cell array was not converted correctly

## [0.0.22] - 2020-05-18

### Fixed

- Add support for complex numbers
- Use up-to-date matrix from string generation function of numpy
- String handling is more stable and consistent for 7.3 files
- No more crashes when importing complex types like classes. Instead a warning is shown


## [0.0.20] - 2019-04-09

### Added

- Releases are tagged automatically on gitlab.

## [0.0.19] - 2019-03-06

### Changed

- Corrected handling of matlab uint64 type
- Reverted pinning version of conda build

## [0.0.18] - 2019-01-08

### Changed

- Accessing the value of a h5py object using `.value` has been deprecated. This is fixed.
- CIs including codecov now also work when the repository is forked.

## [0.0.17] - 2018-08-30

### Changed

- Handling of empty cell arrays is now harmonized.

## [0.0.16] - 2018-08-22

### Changed

- Improvements of maintainability in makefile

## [0.0.15] - 2018-08-22

### Added

- Changelog file

### Changed

- Updated documentation