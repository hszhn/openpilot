# 2015 别克昂科威 C3 维护基线

本文档只适用于车主已完成路试的 2015 别克昂科威。更新 openpilot 、更换分支或重置 C3 后，必须保留以下条件。

## 安装

C3 自定义软件地址：

```text
installer.comma.ai/hszhn/C3-2015-Envision
```

GitHub 分支：`hszhn/openpilot` 的 `C3-2015-Envision`。原始 `ENVISION/f89392b` 只用于历史对照，不作为新设备的首选安装分支。

## 必要车型条件

- 新版车型常量必须是独立的 `BUICK_ENVISION_2015`，不再与 2020–2023 车型共用指纹。
- `BUICK_BABYENCLAVE` 仅作旧开发名称的兼容路径，保证旧缓存和历史安装可继续启动。
- 旧 `ENVISION/f89392b` 的持久化车型名是 `BUICK BABY ENCLAVE 2020`。
- 必须保留 `selfdrive/car/gm/fingerprints.py` 中的 2015 昂科威实测指纹，否则干净安装可能得到 `car_fingerprint=null`。
- 旧版恢复后如仍无法识别，将 `CarModel` 设为 `BUICK BABY ENCLAVE 2020`，将 `ForceFingerprint` 设为 `1`，并清除 `CarParamsCache` 和 `CarParamsPersistent` 后重启。
- SDGM 布线使用动力 CAN bus 0 和摄像头/按键 CAN bus 2；该 C3 使用单个内置 Panda，不启用 `UseRedPanda`。

## 必要控制逻辑

- `networkLocation` 必须为 `fwdCamera`，`pcmCruise` 必须为 `True`。
- 本车的 `ACCCruiseState` 长期为 `0`，不能用它单独判断自适应巡航。
- `is_non_adaptive_cruise()` 对 `BUICK_ENVISION_2015` 及旧兼容名称必须使用 `ACCCmdActive` 判断原车 ACC 是否活动。否则会反复产生 `wrongCruiseMode` 和 `Adaptive Cruise Disabled`。
- 保留 2015 昂科威的车重、轴距、转向线性、变道柔化和 CSLC 速度平滑修复；不要用其它 GM 车型参数覆盖。

## 启动验证

只有以下项目全部通过，才可以进行低速路试：

1. `CarParams` 和 `ControlsReady` 已生成。
2. `controlsd`、`pandad`、`modeld`、`soundd` 持续运行，无反复退出。
3. P 挡时 `gearShifter=park`、`vEgo=0`、`controlsState.enabled=False`。
4. Panda 的 `harnessStatus=normal`、`faultStatus=none`、`heartbeatLost=False`。
5. 开启原车巡航主开关后，`cruiseState.available=True`。
6. 实际 SET 后不得出现 `wrongCruiseMode`、`Adaptive Cruise Disabled` 或 Panda 故障。

## 停车首页

- 左侧“全部行驶统计”直接读取本机 `FrogPilotStats`，并从旧版 `/cache/tracking` 自动迁移总次数、总里程和总时间。
- “过去一周”从本机 `DailyDriveStats` 按日汇总，只保留当天及前 6 天，不依赖 comma 云端。改版前未保存速度的旧日志不做距离估算。
- 右侧保留驾驶模式按钮，移除 comma prime 订阅和 uploading 提示。
- 右侧状态区显示车型识别、控制就绪、设备温度、风扇转速和可用存储。
- 系统请求散热但风扇仍为 `0 RPM` 时，首页必须显示红色故障。

## 散热安全条件

风扇是必要硬件，不得通过提高温度上限规避故障。

- 2026-09-12 诊断时，温控目标曾为 `59%`，Panda 风扇 PWM 达到 `100%`，但实际转速为 `0 RPM`，`fanStallCount` 持续增加。
- 出现上述状态时必须停止路试，检查风扇本体、插头、异物和供电。
- 路试前必须确认高温时 `fanSpeedRpm > 0`，且无黄色/红色过热状态。

## 已验证恢复记录

2026-09-12，旧 `ENVISION/f89392b` 恢复后首次启动无 `CarParams`，`controlsd` 退出。固定 `CarModel`、启用 `ForceFingerprint`、清除车型缓存并重启后，`CarParams`/`ControlsReady` 正常生成，`controlsd` 与 `soundd` 持续运行。车主随后确认 openpilot 路试工作正常。
