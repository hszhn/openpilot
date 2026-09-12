#!/usr/bin/env python3
import argparse
import hashlib
from pathlib import Path


EXPECTED_SHA256 = "f4eeb80b4dbb2eea07c724939c7a21d7909c688863ad28cc751339cc0a5792f1"
EXPECTED_OUTPUT_SHA256 = "231bb8239212d00c4f75c44b151736c1813d54538d2ea668b66fec438c9881b1"


REPLACEMENTS = {
    "Adjustable Personalities": "可调驾驶风格",
    "Use the 'Distance' button on the steering wheel or the onroad UI to switch between openpilot's driving personalities.": "使用方向盘跟车距离键或驾驶界面切换 openpilot 驾驶风格。",
    "1 bar = Aggressive": "1 格 = 激进",
    "2 bars = Standard": "2 格 = 标准",
    "3 bars = Relaxed": "3 格 = 舒缓",
    "Always on Lateral": "始终横向",
    "Maintain openpilot lateral control when the brake or gas pedals are used.": "踩制动或油门踏板时仍保持 openpilot 横向控制。",
    "Deactivation occurs only through the 'Cruise Control' button.": "仅可通过巡航控制按钮关闭。",
    "Enable On Cruise Main": "巡航主开关启用",
    "Enable 'Always On Lateral' by simply turning on 'Cruise Control'.": "开启巡航主开关时启用始终横向控制。",
    "Hide the Status Bar": "隐藏状态栏",
    "Don't use the status bar for 'Always On Lateral'.": "始终横向控制不显示状态栏提示。",
    "Conditional Experimental Mode": "预设场景试验模式",
    "Automatically switches to 'Experimental Mode' under predefined conditions.": "根据预设条件自动切换到试验模式。",
    "Curve Detected Ahead": "前方弯道",
    "Switch to 'Experimental Mode' when a curve is detected.": "检测到弯道时切换到试验模式。",
    "Navigation Based": "基于导航",
    "Switch to 'Experimental Mode' based on navigation data. (i.e. Intersections, stop signs, etc.)": "根据导航信息切换到试验模式，例如路口和停车标志。",
    "Slower Lead Detected Ahead": "检测到前方慢车",
    "Switch to 'Experimental Mode' when a slower lead vehicle is detected ahead.": "检测到前方慢车时切换到试验模式。",
    "Stop Lights and Stop Signs": "红绿灯及停车标志",
    "Switch to 'Experimental Mode' when a stop light or stop sign is detected.": "检测到红绿灯或停车标志时切换到试验模式。",
    "Turn Signal When Below Highway Speeds": "低于高速车速时打转向灯",
    "Switch to 'Experimental Mode' when using turn signals below highway speeds to help assit with turns.": "低于高速车速打转向灯时切换到试验模式，辅助车辆转弯。",
    "Don't use the status bar for 'Conditional Experimental Mode'.": "预设场景试验模式不显示状态栏提示。",
    "Custom Driving Personalities": "自定义驾驶风格",
    "Customize the driving personality profiles to your driving style.": "按照驾驶习惯调整跟车距离参数。",
    "Configure the timer for automatic device shutdown when offroad conserving energy and preventing battery drain.": "设置车辆熄火后设备自动关机的等待时间，以节省电量并防止电瓶亏电。",
    "Device Shutdown Timer": "设备关机计时",
    "Experimental Mode Activation": "试验模式启用方式",
    "Toggle Experimental Mode with either buttons on ethe steering wheel or the screen.": "可通过方向盘按键或屏幕切换试验模式。",
    "Overrides 'Conditional Experimental Mode'.": "优先于预设场景试验模式。",
    "Double Clicking the LKAS Button": "双击 LKAS 按钮",
    "Enable/disable 'Experimental Mode' by double clicking the 'LKAS' button on your steering wheel.": "双击方向盘 LKAS 按钮开启或关闭试验模式。",
    "Double Taping the Onroad UI": "双击驾驶界面",
    "Enable/disable 'Experimental Mode' by double taping the onroad UI within a 0.5 second time frame.": "在 0.5 秒内双击驾驶界面，开启或关闭试验模式。",
    "Long Pressing the Distance Button": "长按跟车距离按钮",
    "Enable/disable 'Experimental Mode' by holding down the 'distance' button on your steering wheel for 0.5 seconds.": "长按方向盘跟车距离按钮 0.5 秒，开启或关闭试验模式。",
    "Fire the Babysitter": "解除安全限制",
    "Deactivate some of openpilot's 'Babysitter' protocols for more user autonomy.": "关闭部分 openpilot 安全限制，提供更多自主控制。",
    "Bypass Thermal Safety Limits": "绕过温度安全限制",
    "Allow the device to run at any temperature even above comma's recommended thermal limits.": "允许设备在超过 comma 建议温度限制时继续运行。",
    "Disable Logging": "禁用日志",
    "Turn off all data tracking to enhance privacy or reduce thermal load.": "关闭所有数据记录，以保护隐私或降低设备负载。",
    "WARNING: This action will prevent drive recording and data cannot be recovered!": "警告：此操作会停止行程记录，数据无法恢复！",
    "Disable Dashcam": "禁用录像",
    "Turn off dashcam recording to enhance privacy or reduce thermal load.": "关闭行车录像，以保护隐私或降低设备负载。",
    "WARNING: Only qlog and rlog will be logged!": "警告：仅记录 qlog 和 rlog！",
    "Disable Uploads": "禁止上传",
    "Turn off all data uploads to comma's servers.": "停止向 comma 上传数据。",
    "WARNING: This action will prevent your drives from appearing on comma connect which may impact debugging and support!": "警告：行程将不会显示在 comma connect，可能影响故障排查和支持！",
    "Offline Mode": "离线模式",
    "Allow the device to be offline indefinitely.": "允许设备长期保持离线。",
    "Lateral Tuning": "横向调校",
    "Modify openpilot's steering behavior.": "调整 openpilot 的转向控制。",
    "Force Auto Tune": "强制自调",
    "Forces comma's auto lateral tuning for unsupported vehicles.": "为不支持车辆强制使用 comma 横向自调。",
    "NNFF - Neural Network Feedforward": "NNFF 神经网络前馈",
    "Use Twilsonco's Neural Network Feedforward for enhanced precision in lateral control.": "使用 Twilsonco 神经网络前馈，提高横向控制精度。",
    "Steer Ratio (Default: %1)": "转向比（默认 %1）",
    "Steer Ratio": "转向比",
    "Set a custom steer ratio for your vehicle controls.": "为本车设置自定义转向比。",
    "Use Lateral Jerk": "横向急动度",
    "Include steer torque necessary to achieve desired steer rate (lateral jerk).": "加入达到目标转向速率所需的转向扭矩（横向急动度）。",
    "Longitudinal Tuning": "纵向调校",
    "Modify openpilot's acceleration and braking behavior.": "调整 openpilot 的加速和制动控制。",
    "Acceleration Profile": "加速模式",
    "Change the acceleration rate to be either sporty or eco-friendly.": "选择运动或节能的加速响应。",
    "Deceleration Profile": "减速模式",
    "Change the deceleration rate to be either sporty or eco-friendly.": "选择运动或节能的减速响应。",
    "Increase acceleration aggressiveness when following a lead vehicle from a stop.": "跟随前车起步时提高加速积极性。",
    "Increase Stop Distance Behind Lead": "增加跟车停车距离",
    "Increase the stopping distance for a more comfortable stop from lead vehicles.": "增加与前车的停车距离，使停车更舒适。",
    "Smoother Braking Behind Lead": "跟车制动更平顺",
    "Smoothen out the braking behavior when approaching slower vehicles.": "接近较慢车辆时使制动更平顺。",
    "Traffic Mode": "拥堵模式",
    "Hold down the 'distance' button for 2.5 seconds to enable more aggressive driving behavior catered towards stop and go traffic.": "长按跟车距离按钮 2.5 秒，启用适合走走停停路况的积极驾驶模式。",
    "Model Selector": "模型选择",
    "Choose your preferred openpilot model.": "选择 openpilot 驾驶模型。",
    "Calibration Cycles": "校准循环次数",
    "Choose your calibration cycles, larger number needs more time to calibration.": "设置模型校准循环次数，数值越大，校准时间越长。",
    "Map Turn Speed Control": "地图弯道限速",
    "Slow down for anticipated curves detected by your downloaded maps.": "根据已下载地图识别前方弯道并提前减速。",
    "Disable MTSC UI Smoothing": "关闭 MTSC 界面平滑",
    "Disables the smoothing for the requested speed in the onroad UI.": "关闭驾驶界面对请求速度的平滑显示。",
    "Model Curvature Detection Failsafe": "模型弯道检测保护",
    "Only trigger MTSC when the model detects a curve in the road. Purely used as a failsafe to prevent false positives. Leave this off if you never experience false positives.": "仅在模型检测到道路弯道时触发 MTSC，用于防止地图误判；没有误判时请保持关闭。",
    "Speed Change Hard Cap": "速度变化硬限制",
    "Set a hard cap for MTSC. If MTSC requests a speed decrease greater than this value, it ignores the requested speed from MTSC. Purely used as a failsafe to prevent false positives. Leave this off if you never experience false positives.": "设置 MTSC 减速幅度上限；超过此值时忽略 MTSC 请求，用于防止地图误判。没有误判时请保持关闭。",
    "Turn Speed Aggressiveness": "弯道速度积极度",
    "Set turn speed aggressiveness. Higher values result in faster turns, lower values yield gentler turns.": "设置弯道速度积极度；数值越高过弯越快，越低越平缓。",
    "A change of +- 1% results in the velocity being raised or lowered by about 1 mph.": "每调整正负 1%，弯道速度约变化 1 mph。",
    "Nudgeless Lane Change": "自动变道",
    "Enable lane changes without manual steering input.": "无需手动施加转向力即可变道。",
    "Lane Change Timer": "变道计时",
    "Specify a delay before executing a nudgeless lane change.": "设置自动变道开始前的等待时间。",
    "Lane Detection": "车道检测",
    "Block nudgeless lane changes when a lane isn't detected.": "未检测到目标车道时禁止自动变道。",
    "Lane Detection Threshold": "车道宽度阈值",
    "Set the required lane width to be qualified as a lane.": "设置目标车道必须达到的最小宽度。",
    "One Lane Change Per Signal": "每次打灯一次变道",
    "Limit to one nudgeless lane change per turn signal activation.": "每次开启转向灯只允许自动变道一次。",
    "Smoother Lane Change": "平顺变道",
    "Smoother lane change on start, beware of understeer.": "变道起始更平顺，请注意转向不足。",
    "Quality of Life": "便捷功能",
    "Miscellaneous quality of life changes to improve your overall openpilot experience.": "提供多项便捷设置，改善 openpilot 使用体验。",
    "Disable Onroad Uploads": "行驶时禁止上传",
    "Prevent large data uploads when onroad.": "行驶时禁止大数据上传。",
    "Higher Bitrate Recording": "高码率录像",
    "Increases the quality of the footage uploaded to comma connect.": "提高上传到 comma connect 的录像画质。",
    "Navigate on Chill Mode": "舒缓模式导航",
    "Allows cars without longitudinal support to navigate. Allows navigation without experimental mode.": "允许无纵向控制支持的车辆导航，也可不启用试验模式进行导航。",
    "Temporarily disable lateral control during turn signal use below the set speed.": "低于设定速度使用转向灯时，暂时关闭横向控制。",
    "Standard Min Steer Speed": "标准最低转向速度",
    "Set the standard minimium activative steering speed.": "设置横向控制的标准最低启用速度。",
    "Engaged Min Steer Speed": "接管最低转向",
    "Set the minimium activative steering speed when adaptive cruise control engaged.": "设置自适应巡航接管后横向控制的最低启用速度。",
    "Reverse Cruise Increase": "反向巡航增速",
    "Reverses the 'long press' functionality when increasing the max set speed. Useful to increase the max speed quickly.": "反转提高设定速度时的长按功能，便于快速提高最高设定速度。",
    "Cruise Increase Interval": "巡航增速步长",
    "Set a custom interval to increase the max set speed by.": "设置提高最高巡航速度的步长。",
    "Cruise Increase Interval (Long Press)": "长按巡航增速步长",
    "Set a custom interval to increase the max set speed by when holding down the cruise increase button.": "设置长按巡航增速按钮时提高最高设定速度的步长。",
    "Set Speed Offset": "速度偏移",
    "Set an offset for your desired set speed.": "为目标设定速度增加偏移量。",
    "Speed Limit Controller": "限速控制器",
    "Automatically adjust vehicle speed to match speed limits using 'Open Street Map's, 'Navigate On openpilot', or your car's dashboard (TSS2 Toyotas only).": "根据 OpenStreetMap、openpilot 导航或车辆仪表限速自动调整车速。",
    "Controls Settings": "控制设置",
    "Manage settings for the controls.": "管理限速控制相关设置。",
    "Speed Limit Offset (0-34 mph)": "限速偏移（0-34 mph）",
    "Speed limit offset for speed limits between 0-34 mph.": "限速为 0-34 mph 时使用的偏移量。",
    "Speed Limit Offset (35-54 mph)": "限速偏移（35-54 mph）",
    "Speed limit offset for speed limits between 35-54 mph.": "限速为 35-54 mph 时使用的偏移量。",
    "Speed Limit Offset (55-64 mph)": "限速偏移（55-64 mph）",
    "Speed limit offset for speed limits between 55-64 mph.": "限速为 55-64 mph 时使用的偏移量。",
    "Speed Limit Offset (65-99 mph)": "限速偏移（65-99 mph）",
    "Speed limit offset for speed limits between 65-99 mph.": "限速为 65-99 mph 时使用的偏移量。",
    "Fallback Method": "备用方式",
    "Choose your fallback method for when there are no speed limits currently being obtained from Navigation, OSM, and the car's dashboard.": "导航、OSM 和车辆仪表均无可用限速时，选择备用方式。",
    "Override Method": "覆盖方式",
    "Choose your preferred method to override the current speed limit.": "选择临时覆盖当前限速的方式。",
    "Priority Order": "优先顺序",
    "Determine the priority order for what speed limits to use.": "设置不同限速来源的使用优先顺序。",
    "Quality of Life Settings": "便捷设置",
    "Manage quality of life settings.": "管理便捷设置。",
    "Confirm New Speed Limits": "确认新限速",
    "Don't automatically start using the new speed limit until it's been manually confirmed first.": "新限速需手动确认后才会使用。",
    "Force MPH From Dashboard Readings": "仪表强制使用 MPH",
    "Force MPH readings from the dashboard. Only use this if you live in an area where the speed limits from your dashboard are in KPH but you use MPH.": "强制将仪表限速按 MPH 读取；仅在仪表限速单位识别错误时使用。",
    "Use Current Speed Limit As Set Speed": "将当前限速设为巡航速度",
    "Sets your max speed to the current speed limit if one is populated when you initially enable openpilot.": "启用 openpilot 时若有当前限速，将最高设定速度设为该限速。",
    "Visuals Settings": "显示设置",
    "Manage visual settings.": "管理显示。",
    "Show Speed Limit Offset": "显示限速偏移",
    "Show the speed limit offset seperated from the speed limit in the onroad UI when using 'Speed Limit Controller'.": "使用限速控制器时，在驾驶界面单独显示限速偏移。",
    "Use Vienna Speed Limit Signs": "使用维也纳限速标志",
    "Use the Vienna (EU) speed limit style signs as opposed to MUTCD (US).": "使用欧盟限速标志，不使用美国样式。",
    "Use Turn Desires": "转弯意图",
    "Use turn desires for enhanced precision in turns below the minimum lane change speed.": "低于最低变道速度时使用转弯意图，提高转弯精度。",
    "Vision Turn Speed Controller": "视觉弯道限速",
    "Slow down for detected road curvature for smoother curve handling.": "根据检测到的道路曲率减速，使过弯更平顺。",
    "Disable VTSC UI Smoothing": "关闭 VTSC 界面平滑",
    "Curve Detection Sensitivity": "弯道检测灵敏度",
    "Set curve detection sensitivity. Higher values prompt earlier responses, lower values lead to smoother but later reactions.": "设置弯道检测灵敏度；数值越高响应越早，越低响应更晚但更平顺。",
    "Set the 'Aggressive' personality' following distance. Represents seconds to follow behind the lead vehicle.": "设置激进驾驶风格的跟车距离，以秒表示与前车的时间间隔。",
    "Stock: 1.25 seconds.": "原厂：1.25 秒。",
    "Configure brake/gas pedal responsiveness for the 'Aggressive' personality. Higher jerk value = smoother rides.": "设置激进驾驶风格的制动和油门响应；响应值越高，行驶越平顺。",
    "Lower jerk value = faster response.": "响应值越低，反应越快。",
    "Stock: 0.5.": "原厂 0.5",
    "Set the 'Standard' personality following distance. Represents seconds to follow behind the lead vehicle.": "设置标准驾驶风格的跟车距离，以秒表示与前车的时间间隔。",
    "Stock: 1.45 seconds.": "原厂：1.45 秒。",
    "Adjust brake/gas pedal responsiveness for the 'Standard' personality. Higher jerk value = smoother rides.": "设置标准驾驶风格的制动和油门响应；响应值越高，行驶越平顺。",
    "Stock: 1.0.": "原厂 1.0",
    "Set the 'Relaxed' personality following distance. Represents seconds to follow behind the lead vehicle.": "设置舒缓驾驶风格的跟车距离，以秒表示与前车的时间间隔。",
    "Stock: 1.75 seconds.": "原厂：1.75 秒。",
    "Set brake/gas pedal responsiveness for the 'Relaxed' personality. Higher jerk value = smoother rides.": "设置舒缓驾驶风格的制动和油门响应；响应值越高，行驶越平顺。",
    "Control Via UI": "界面控制",
    "Lower Limits": "较低限速",
    "Higher Limits": "较高限速",
    "Select your primary priority": "选择第一优先来源",
    "Select your secondary priority": "选择第二优先来源",
    "Select your tertiary priority": "选择第三优先来源",
    "Speed Limit Offset (0-24 kph)": "限速偏移（0-24 kph）",
    "Speed Limit Offset (25-60 kph)": "限速偏移（25-60 kph）",
    "Speed Limit Offset (61-90 kph)": "限速偏移（61-90 kph）",
    "Speed Limit Offset (90+ kph)": "限速偏移（90+ kph）",
    "Set speed limit offset for limits between 0-24 kph.": "限速为 0-24 kph 时使用的偏移量。",
    "Set speed limit offset for limits between 25-60 kph.": "限速为 25-60 kph 时使用的偏移量。",
    "Set speed limit offset for limits between 61-90 kph.": "限速为 61-90 kph 时使用的偏移量。",
    "Set speed limit offset for limits above 90+ kph.": "限速高于 90 kph 时使用的偏移量。",
    "Set speed limit offset for limits between 0-34 mph.": "限速为 0-34 mph 时使用的偏移量。",
    "Set speed limit offset for limits between 35-54 mph.": "限速为 35-54 mph 时使用的偏移量。",
    "Set speed limit offset for limits between 55-64 mph.": "限速为 55-64 mph 时使用的偏移量。",
    "Set speed limit offset for limits between 65-99 mph.": "限速为 65-99 mph 时使用的偏移量。",
    "WARNING: This maxes out openpilot's acceleration from 2.0 m/s to 4.0 m/s and may cause oscillations when accelerating!": "警告：此设置会将 openpilot 最大加速度从 2.0 m/s 提高到 4.0 m/s，可能导致加速波动！",
    "I understand the risks.": "已知风险",
    "Select a driving model": "选择驾驶模型",
    "Do you want to start with a fresh calibration for the newly selected model?": "是否为新选择的模型重新开始校准？",
    "Reboot required to take effect.": "需要重启后生效。",
    "WARNING: This isn't guaranteed to work, so if you run into any issues, please report it in the FrogPilot Discord!": "警告：此功能不保证正常工作，如遇问题请反馈到 FrogPilot Discord！",
    "WARNING: This MAY cause premature wear or damage by running the device over comma's recommended temperature limits!": "警告：设备超过 comma 建议温度运行，可能导致提前老化或损坏！",
    "Switch to 'Experimental Mode' below this speed in absence of a lead vehicle.": "无前车时，低于此速度自动切换到试验模式。",
    "Switch to 'Experimental Mode' below this speed when following a lead vehicle.": "跟随前车时，低于此速度自动切换到试验模式。",
}


OFFSET_REPLACEMENTS = {
    0x255022: ("  w/Lead", "  跟车"),
    0x2554FE: ("Instant", "立即"),
    0x25552A: ("Los Angeles (Default)", "洛杉矶（默认）"),
    0x25518A: (" sec", "秒 "),
    0x255506: (" mins", " 分"),
    0x25550C: (" hour", " 时"),
    0x255512: (" hours", "小时"),
    0x25554F: (" seconds", " 秒"),
}

PATCH_START = 0x252AE2
PATCH_END = 0x255B92


def padded(old: str, new: str) -> bytes:
    old_bytes = old.encode("utf-8")
    new_bytes = new.encode("utf-8")
    if len(new_bytes) > len(old_bytes):
        raise ValueError(f"replacement too long: {old!r} -> {new!r}")
    return new_bytes + b" " * (len(old_bytes) - len(new_bytes))


parser = argparse.ArgumentParser(description="Patch the ENVISION/f89392b UI with complete Chinese driving-control text.")
parser.add_argument("source", type=Path, help="unmodified legacy UI executable")
parser.add_argument("output", type=Path, help="patched UI output path")
args = parser.parse_args()

data = bytearray(args.source.read_bytes())
actual_sha256 = hashlib.sha256(data).hexdigest()
if actual_sha256 != EXPECTED_SHA256:
    raise RuntimeError(f"unexpected source SHA256: {actual_sha256}")

for old, new in sorted(REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True):
    old_bytes = old.encode("utf-8")
    starts = []
    cursor = PATCH_START
    while True:
        start = data.find(old_bytes, cursor, PATCH_END)
        if start < 0:
            break
        starts.append(start)
        cursor = start + len(old_bytes)
    if not starts:
        raise RuntimeError(f"no control-settings occurrence of {old!r}")
    for start in starts:
        data[start:start + len(old_bytes)] = padded(old, new)
        print(f"0x{start:08x}: {old} -> {new}")

# Two display labels share storage with longer titles. Keep each title and its
# suffix label independently NUL-terminated so both call sites remain valid.
aggressive = 0x253A37
with_lead = 0x253A4F
data[aggressive:with_lead] = "前车积极加速".encode() + b"\0" * ((with_lead - aggressive) - len("前车积极加速".encode()))
data[with_lead:with_lead + 10] = "有前车".encode() + b"\0"

pause_title = 0x25441E
below = 0x25443B
data[pause_title:below] = "转向灯暂停横向".encode() + b"\0" * ((below - pause_title) - len("转向灯暂停横向".encode()))
data[below:below + 6] = "低".encode() + b"  \0"

# "Follow" is pooled inside the internal key "RelaxedFollow", and " Jerk" is
# pooled inside another title. Redirect only the six visible profile labels to
# dedicated Chinese strings, leaving parameter names untouched.
follow_text = 0x255138
jerk_text = 0x25316A
data[follow_text:follow_text + 7] = "跟车".encode() + b"\0"
data[jerk_text:jerk_text + 7] = "响应".encode() + b"\0"

def patch_instruction(offset: int, expected_hex: str, replacement_hex: str) -> None:
    expected = bytes.fromhex(expected_hex)
    replacement = bytes.fromhex(replacement_hex)
    if data[offset:offset + 4] != expected:
        raise RuntimeError(f"instruction mismatch at 0x{offset:x}")
    data[offset:offset + 4] = replacement

# ADD X0, X0, #0x3a9 -> #0x138 (three "Follow" labels)
for offset in (0x104840, 0x104CBC, 0x105138):
    patch_instruction(offset, "00a40e91", "00e00491")

# ADD X0, X0, #0x8b0 -> #0x16a, followed by title byte length 5 -> 6.
for offset in (0x104A64, 0x104EE0, 0x105358):
    patch_instruction(offset, "00c02291", "00a80591")
    patch_instruction(offset + 4, "a1008052", "c1008052")

for offset, (old, new) in OFFSET_REPLACEMENTS.items():
    old_bytes = old.encode("utf-8")
    if data[offset:offset + len(old_bytes)] != old_bytes:
        found = bytes(data[offset:offset + len(old_bytes)])
        raise RuntimeError(f"offset 0x{offset:x}: expected {old_bytes!r}, found {found!r}")
    data[offset:offset + len(old_bytes)] = padded(old, new)
    print(f"0x{offset:08x}: {old} -> {new}")

if len(data) != args.source.stat().st_size:
    raise RuntimeError("output size changed")

output_sha256 = hashlib.sha256(data).hexdigest()
if output_sha256 != EXPECTED_OUTPUT_SHA256:
    raise RuntimeError(f"unexpected output SHA256: {output_sha256}")

args.output.write_bytes(data)
args.output.chmod(0o755)
print(f"size={len(data)}")
print(f"sha256={output_sha256}")
