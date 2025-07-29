# Copyright 2025 DeepMind Technologies Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Base classes for Apollo."""

from typing import Any, Dict, Optional, Union

import jax
import jax.numpy as jp
import mujoco
import numpy as np
from etils import epath
from ml_collections import config_dict
from mujoco import mjx

from mujoco_playground._src import mjx_env
from mujoco_playground._src.locomotion.apollo import constants as consts
from mujoco_playground._src.collision import geoms_colliding


def get_assets() -> Dict[str, bytes]:
  assets = {}
  # Playground assets.
  mjx_env.update_assets(assets, consts.XML_DIR, "*.xml")
  mjx_env.update_assets(assets, consts.XML_DIR / "assets")
  # Menagerie assets.
  path = mjx_env.MENAGERIE_PATH / "apptronik_apollo"
  mjx_env.update_assets(assets, path, "*.xml")
  mjx_env.update_assets(assets, path / "assets")
  mjx_env.update_assets(assets, path / "assets" / "ability_hand")
  return assets


class ApolloEnv(mjx_env.MjxEnv):
  """Base class for Apollo environments."""

  def __init__(
    self,
    xml_path: str,
    config: config_dict.ConfigDict,
    config_overrides: Optional[Dict[str, Union[str, int, list[Any]]]] = None,
  ) -> None:
    super().__init__(config, config_overrides)

    self._mj_model = mujoco.MjModel.from_xml_string(
      epath.Path(xml_path).read_text(), assets=get_assets()
    )
    self._mj_model.opt.timestep = self.sim_dt

    self._mj_model.vis.global_.offwidth = 3840
    self._mj_model.vis.global_.offheight = 2160

    self._mjx_model = mjx.put_model(self._mj_model)
    self._xml_path = xml_path

    self._init_q = jp.array(self._mj_model.keyframe("knees_bent").qpos)
    self._default_ctrl = jp.array(self._mj_model.keyframe("knees_bent").ctrl)
    self._default_pose = jp.array(self._mj_model.keyframe("knees_bent").qpos[7:])
    self._actuator_torques = self.mj_model.jnt_actfrcrange[1:, 1]

    # Body IDs.
    self._torso_body_id = self._mj_model.body(consts.ROOT_BODY).id

    # Geom IDs.
    self._floor_geom_id = self._mj_model.geom("floor").id
    self._left_feet_geom_id = np.array(
      [self._mj_model.geom(name).id for name in consts.LEFT_FEET_GEOMS]
    )
    self._right_feet_geom_id = np.array(
      [self._mj_model.geom(name).id for name in consts.RIGHT_FEET_GEOMS]
    )
    self._left_hand_geom_id = self._mj_model.geom("collision_l_hand_plate").id
    self._right_hand_geom_id = self._mj_model.geom("collision_r_hand_plate").id
    self._left_foot_geom_id = self._mj_model.geom("collision_l_sole").id
    self._right_foot_geom_id = self._mj_model.geom("collision_r_sole").id
    self._left_shin_geom_id = self._mj_model.geom("collision_capsule_body_l_shin").id
    self._right_shin_geom_id = self._mj_model.geom("collision_capsule_body_r_shin").id
    self._left_thigh_geom_id = self._mj_model.geom("collision_capsule_body_l_thigh").id
    self._right_thigh_geom_id = self._mj_model.geom("collision_capsule_body_r_thigh").id

    # Site IDs.
    self._imu_site_id = self._mj_model.site("imu").id
    self._feet_site_id = np.array(
      [self._mj_model.site(name).id for name in consts.FEET_SITES]
    )

  # Sensor readings.

  def get_gravity(self, data: mjx.Data) -> jax.Array:
    """Return the gravity vector in the world frame."""
    return mjx_env.get_sensor_data(self.mj_model, data, f"{consts.GRAVITY_SENSOR}")

  def get_global_linvel(self, data: mjx.Data) -> jax.Array:
    """Return the linear velocity of the robot in the world frame."""
    return mjx_env.get_sensor_data(
      self.mj_model, data, f"{consts.GLOBAL_LINVEL_SENSOR}"
    )

  def get_global_angvel(self, data: mjx.Data) -> jax.Array:
    """Return the angular velocity of the robot in the world frame."""
    return mjx_env.get_sensor_data(
      self.mj_model, data, f"{consts.GLOBAL_ANGVEL_SENSOR}"
    )

  def get_local_linvel(self, data: mjx.Data) -> jax.Array:
    """Return the linear velocity of the robot in the local frame."""
    return mjx_env.get_sensor_data(self.mj_model, data, f"{consts.LOCAL_LINVEL_SENSOR}")

  def get_accelerometer(self, data: mjx.Data) -> jax.Array:
    """Return the accelerometer readings in the local frame."""
    return mjx_env.get_sensor_data(
      self.mj_model, data, f"{consts.ACCELEROMETER_SENSOR}"
    )

  def get_gyro(self, data: mjx.Data) -> jax.Array:
    """Return the gyroscope readings in the local frame."""
    return mjx_env.get_sensor_data(self.mj_model, data, f"{consts.GYRO_SENSOR}")

  def get_feet_ground_contacts(self, data: mjx.Data) -> jax.Array:
    """Return an array indicating whether each foot is in contact with the ground."""
    left_feet_contact = jp.array(
      [
        geoms_colliding(data, geom_id, self._floor_geom_id)
        for geom_id in self._left_feet_geom_id
      ]
    )
    right_feet_contact = jp.array(
      [
        geoms_colliding(data, geom_id, self._floor_geom_id)
        for geom_id in self._right_feet_geom_id
      ]
    )
    return jp.hstack([jp.any(left_feet_contact), jp.any(right_feet_contact)])

  # Accessors.

  @property
  def xml_path(self) -> str:
    return self._xml_path

  @property
  def action_size(self) -> int:
    return self._mjx_model.nu

  @property
  def mj_model(self) -> mujoco.MjModel:
    return self._mj_model

  @property
  def mjx_model(self) -> mjx.Model:
    return self._mjx_model
