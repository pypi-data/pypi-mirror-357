import typing
import enum
import copy

T = typing.TypeVar("T")

_merge_sentinel = object()
_target_sentinel = object()


class ReplaceMode(enum.Enum):
    REPLACING = 1
    FIRST_ONLY = 2
    MERGING = 4


def key_migrate(instance: dict[T, object], current: T, goal: T, deleting=True) -> bool:
    if current not in instance:
        return False
    key_merge(
        instance,
        current,
        target=goal,
        repl_mode=ReplaceMode.REPLACING,
        deleting=deleting,
    )
    return True


def key_merge(
    o: dict[T, object],
    *keys: T,
    target: T | object = _target_sentinel,
    repl_mode: ReplaceMode = ReplaceMode.FIRST_ONLY,
    deleting: bool = True,
    in_place: bool = True,
):
    if not in_place:
        o = copy.deepcopy(o)

    if repl_mode == ReplaceMode.FIRST_ONLY or repl_mode == ReplaceMode.REPLACING:
        result = _merge_sentinel
    elif repl_mode == ReplaceMode.MERGING:
        result = []

    # handle the case where target exists in the dictionary
    if target in o and target not in keys:
        keys = keys + (target,)

    last_key = _merge_sentinel
    for k in keys:
        if k in o:
            last_key = k
            value = o[k]
            if (
                repl_mode == ReplaceMode.FIRST_ONLY and result is _merge_sentinel
            ) or repl_mode == ReplaceMode.REPLACING:
                result = value
            elif repl_mode == ReplaceMode.MERGING:
                typing.cast(list[T], result).append(value)
            if deleting:
                del o[k]

    if target is _target_sentinel:
        if repl_mode == ReplaceMode.FIRST_ONLY or repl_mode == ReplaceMode.MERGING:
            if last_key is _merge_sentinel:
                if repl_mode == ReplaceMode.MERGING:
                    o[keys[0]] = []
                return o
            k = keys[0]
            o[k] = result
            return o
        if repl_mode == ReplaceMode.REPLACING:
            if last_key is not _merge_sentinel:
                last_key = typing.cast(T, last_key)
                o[last_key] = result
            return o
        assert False, "Missing ENUM case {}".format(repl_mode)
    else:
        target = typing.cast(T, target)
        if result == _merge_sentinel:
            if repl_mode == ReplaceMode.MERGING:
                o[target] = []
        else:
            o[target] = result
        return o
