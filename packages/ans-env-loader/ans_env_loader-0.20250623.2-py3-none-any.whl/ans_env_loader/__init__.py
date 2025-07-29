# vars_plugins/import_env_vars.py

import os
from pathlib import Path

from ansible.errors import AnsibleError
from ansible.plugins.vars import BaseVarsPlugin


class VarsModule(BaseVarsPlugin):
    def get_vars(self, loader, path, entities, cache=True):
        env_vars_path = Path(path) / 'ans-env-vars.yaml'

        if not env_vars_path.exists():
            raise AnsibleError('Expected "ans-env-vars.yaml" to exist')

        line_items = loader.load_from_file(env_vars_path.as_posix())
        if not isinstance(line_items, list):
            raise AnsibleError(
                'Expected "ans-env-vars.yaml" to be a list of strings',
            )

        missing = []
        result = {}
        for item in line_items:
            if isinstance(item, dict):
                ans_var_name, env_var_name = next(iter(item.items()))
            else:
                assert isinstance(item, str)
                ans_var_name = item
                env_var_name = item

            env_val = os.environ.get(env_var_name)
            if env_val is None:
                missing.append(env_var_name)
            else:
                result[ans_var_name] = env_val

        if missing:
            raise AnsibleError('Required env variables not set: {}'.format(', '.join(missing)))

        return result
