#!/usr/bin/env bats

@test "percentile input output" {
  TEST_DIR=$(mktemp -d)
  if [[ -z "${IMPROVER_ACC_TEST_DIR:-}" ]]; then
    skip "Acceptance test directory not defined"
  fi
  if ! type -f nccmp 1>/dev/null 2>&1; then
    skip "nccmp not installed"
  fi
  # Run percentile conversion and check it passes.
  run improver percentile \
      "$IMPROVER_ACC_TEST_DIR/percentile/basic/input.nc" "$TEST_DIR/output.nc"
  [[ "$status" -eq 0 ]]

  # Run nccmp to compare the output and kgo.
  run nccmp -dmNs "$TEST_DIR/output.nc" \
      "$IMPROVER_ACC_TEST_DIR/percentile/basic/kgo.nc"
  [[ "$status" -eq 0 ]]
  [[ "$output" =~ "are identical." ]]
  rm "$TEST_DIR/output.nc"
  rmdir "$TEST_DIR"
}

