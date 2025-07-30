#!/bin/bash

# This script determines which manually specified packages have changes
# and prepares a matrix for GitHub Actions.

# Section 1: Configuration & Initial Checks
# $ALL_CHANGED_FILES is expected to be passed as an environment variable by the workflow.
# $PACKAGES_TO_LINT is expected to be passed as a space-separated string of package directories.

echo "All changed files (from action): $ALL_CHANGED_FILES"
echo "Packages to lint (from workflow): $PACKAGES_TO_LINT"

# Convert the space-separated PACKAGES_TO_LINT string into a bash array.
if [ -z "$PACKAGES_TO_LINT" ]; then
  echo "PACKAGES_TO_LINT environment variable is not set or is empty."
  all_project_pkg_dirs=()
else
  read -r -a all_project_pkg_dirs <<< "$PACKAGES_TO_LINT"
fi

echo "Manually specified package directories to monitor: ${all_project_pkg_dirs[*]}"

# If no packages are specified, exit early.
if [ ${#all_project_pkg_dirs[@]} -eq 0 ]; then
  echo "No package directories specified. Exiting."
  json_payload_for_matrix="{\"include\":[]}"
  echo "Full JSON payload for matrix (empty): $json_payload_for_matrix" # For debugging

  echo "matrix<<MATRIX_JSON_EOF" >> "$GITHUB_OUTPUT"
  echo "${json_payload_for_matrix}" >> "$GITHUB_OUTPUT"
  echo "MATRIX_JSON_EOF" >> "$GITHUB_OUTPUT"
  
  echo "has_changed_packages=false" >> "$GITHUB_OUTPUT"
  exit 0
fi

# Section 2: Determine Which Specified Packages Have Changed
# Convert the string of all changed files (space-separated) into a bash array.
read -r -a changed_files_array <<< "$ALL_CHANGED_FILES"

if [ ${#changed_files_array[@]} -eq 0 ]; then
  echo "No files were reported as changed by the action."
fi

final_changed_pkgs_for_matrix=() # Array to store packages that have actual changes.
has_any_changed_pkg=false      # Flag to track if at least one package has changes.

# Iterate through each manually specified package directory.
for proj_pkg_dir in "${all_project_pkg_dirs[@]}"; do
  pkg_has_diff=false # Flag for the current package.
  # Iterate through each file reported as changed.
  for changed_file in "${changed_files_array[@]}"; do
    # Check if the changed file is within the current package directory.
    if [[ "$changed_file" == "$proj_pkg_dir/"* || "$changed_file" == "$proj_pkg_dir" ]]; then
      pkg_has_diff=true
      break # Found a change in this package, no need to check other files for it.
    fi
  done

  if $pkg_has_diff; then
    echo "Package '$proj_pkg_dir' has changes."
    final_changed_pkgs_for_matrix+=("{\"package_dir\":\"$proj_pkg_dir\"}")
    has_any_changed_pkg=true
  else
    echo "Package '$proj_pkg_dir' has no changes."
  fi
done

# Section 3: Set GitHub Actions Outputs
# Based on whether any specified packages had changes, prepare the output matrix.
if $has_any_changed_pkg; then
  matrix_json_include_part=$(IFS=,; echo "[${final_changed_pkgs_for_matrix[*]}]")
  # Construct the full JSON payload for the matrix
  json_payload_for_matrix="{\"include\":${matrix_json_include_part}}"
  
  echo "Final matrix include list: $matrix_json_include_part" # For debugging
  echo "Full JSON payload for matrix: $json_payload_for_matrix" # For debugging
  
  echo "matrix<<MATRIX_JSON_EOF" >> "$GITHUB_OUTPUT"
  echo "${json_payload_for_matrix}" >> "$GITHUB_OUTPUT"
  echo "MATRIX_JSON_EOF" >> "$GITHUB_OUTPUT"
else
  echo "No manually specified packages have changes based on the changed files list."
  
  # Construct the empty JSON payload for the matrix
  json_payload_for_matrix="{\"include\":[]}"
  echo "Full JSON payload for matrix (empty): $json_payload_for_matrix" # For debugging

  echo "matrix<<MATRIX_JSON_EOF" >> "$GITHUB_OUTPUT"
  echo "${json_payload_for_matrix}" >> "$GITHUB_OUTPUT"
  echo "MATRIX_JSON_EOF" >> "$GITHUB_OUTPUT"
fi
echo "has_changed_packages=$has_any_changed_pkg" >> "$GITHUB_OUTPUT" 