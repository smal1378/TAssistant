import io
import pickle


class RestrictedUnpickler(pickle.Unpickler):
    allowed = {
        "model": {"Student", "StudentManager",
                  "WeekStructure", "DayStructure",
                  "PlotResult", "Scanner", "Core"}
    }

    def find_class(self, module, name):
        # Only allow safe classes from builtins.
        if module in self.allowed and name in self.allowed[module]:
            return getattr(__import__(module), name)
        # Forbid everything else.
        raise pickle.UnpicklingError("global '%s.%s' is forbidden" %
                                     (module, name))


def loads(s):
    """Helper function analogous to pickle.loads()."""
    return RestrictedUnpickler(io.BytesIO(s)).load()

