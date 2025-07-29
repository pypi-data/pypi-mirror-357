import os 

def make_new_name(file_path: str, new_name: str, *, ext_can_change: bool = True, remove_ext: bool = True) -> str:
    if not ext_can_change and remove_ext:
        raise ValueError("Cannot remove extension if ext_can_change is False.")

    if os.sep in new_name:
        raise ValueError(
            f"New name cannot contain path separators ('{os.sep}').")

    last = file_path.rfind(os.sep, 1)
    if last == -1:
        path, filename = '', file_path
    else:
        path, filename = file_path.rsplit(os.sep, 1)

    _, ext = filename.rsplit('.', 1)

    if '.' in new_name:
        if not ext_can_change:
            _, new_ext = new_name.rsplit('.', 1)
            if new_ext and new_ext != ext:
                raise ValueError("New extension != original extension.")
        return os.sep.join(i for i in [path, new_name] if i)

    if '.' in filename and not remove_ext:
        return os.sep.join(i for i in [path, f"{new_name}.{ext}"] if i)
    else:
        return os.sep.join(i for i in [path, new_name] if i)