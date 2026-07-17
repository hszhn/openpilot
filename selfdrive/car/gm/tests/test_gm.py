from parameterized import parameterized

from openpilot.selfdrive.car.gm.fingerprints import FINGERPRINTS
from openpilot.selfdrive.car.gm.carstate import is_non_adaptive_cruise
from openpilot.selfdrive.car.gm.values import CAR, CAMERA_ACC_CAR, GM_RX_OFFSET

CAMERA_DIAGNOSTIC_ADDRESS = 0x24b


class TestGMFingerprint:
  @parameterized.expand(FINGERPRINTS.items())
  def test_can_fingerprints(self, car_model, fingerprints):
    assert len(fingerprints) > 0

    assert all(len(finger) for finger in fingerprints)

    # The camera can sometimes be communicating on startup
    if car_model in CAMERA_ACC_CAR:
      for finger in fingerprints:
        for required_addr in (CAMERA_DIAGNOSTIC_ADDRESS, CAMERA_DIAGNOSTIC_ADDRESS + GM_RX_OFFSET):
          assert finger.get(required_addr) == 8, required_addr


class TestGMCruiseState:
  @parameterized.expand([
    ("envision_cruise_off", CAR.BUICK_BABYENCLAVE, False, 0, False, False),
    ("envision_acc_active", CAR.BUICK_BABYENCLAVE, True, 0, True, False),
    ("envision_non_acc_active", CAR.BUICK_BABYENCLAVE, True, 0, False, True),
    ("standard_adaptive", "OTHER_GM", True, 2, False, False),
    ("standard_non_adaptive", "OTHER_GM", True, 4, True, True),
  ])
  def test_non_adaptive_cruise(self, _, fingerprint, cruise_enabled, acc_cruise_state, acc_cmd_active, expected):
    assert is_non_adaptive_cruise(fingerprint, cruise_enabled, acc_cruise_state, acc_cmd_active) == expected
