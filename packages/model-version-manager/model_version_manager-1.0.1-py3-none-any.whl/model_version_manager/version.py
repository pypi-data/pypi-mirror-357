from functools import total_ordering

@total_ordering
class Version:
    def __init__(self, *args):
        """Initialize a new Version object with version components.
        
        Supports multiple constructor signatures similar to C#'s Version class:
        
        .. code-block:: python

            Version()                     # 0.0
            Version(major, minor)         # major.minor
            Version(major, minor, build)  # major.minor.build
            Version(major, minor, build, revision)  # major.minor.build.revision
            Version(version_str)          # parses string like "1.2.3.4"

        :param args: Version components (variable arguments)
        :type args: int | str
        :raises ValueError: If any version component is negative
        :raises TypeError: If invalid arguments are provided
        :raises ValueError: If version string is in invalid format
        
        Example usage:
        
        .. code-block:: python

            v1 = Version()               # creates 0.0
            v2 = Version(1, 2)           # creates 1.2
            v3 = Version(1, 2, 3)        # creates 1.2.3
            v4 = Version(1, 2, 3, 4)     # creates 1.2.3.4
            v5 = Version("1.2.3.4")      # parses string
        
        Note:
            Missing components (build, revision) are set to -1 when not provided.
            String parsing follows C# .NET Version string format rules.
        """
        if len(args) == 0:
            self._major = 0
            self._minor = 0
            self._build = -1
            self._revision = -1
            return
        
        # Обработка конструктора из строки
        if len(args) == 1 and isinstance(args[0], str):
            parts = args[0].split('.')
            if not 2 <= len(parts) <= 4:
                raise ValueError("Version string must have 2-4 components")
            try:
                parts = [int(p) for p in parts]
            except ValueError:
                raise ValueError("Version components must be integers")
            
            self._major = parts[0]
            self._minor = parts[1]
            self._build = parts[2] if len(parts) > 2 else -1
            self._revision = parts[3] if len(parts) > 3 else -1
            self._validate_components()
            return
        
        # Обработка числовых конструкторов
        if 2 <= len(args) <= 4:
            if not all(isinstance(x, int) for x in args):
                raise TypeError("Version components must be integers")
            
            self._major = args[0]
            self._minor = args[1]
            self._build = args[2] if len(args) > 2 else -1
            self._revision = args[3] if len(args) > 3 else -1
            self._validate_components()
            return
        
        raise TypeError("Invalid arguments for Version constructor")


    def _validate_components(self):
        """Валидация компонентов версии.
        
        Проверяет что:
        - major и minor неотрицательные
        - build и revision либо -1 (не заданы), либо неотрицательные
        
        :raises ValueError: Если любое из условий не выполняется
        """
        if self._major < 0:
            raise ValueError("Major version must be non-negative")
        if self._minor < 0:
            raise ValueError("Minor version must be non-negative")
        if self._build != -1 and self._build < 0:
            raise ValueError("Build version must be non-negative or -1")
        if self._revision != -1 and self._revision < 0:
            raise ValueError("Revision must be non-negative or -1")

    @staticmethod
    def _validate_non_negative(value, param_name):
        if value < 0:
            raise ValueError(f"ArgumentOutOfRange_Version: {param_name} cannot be negative")

    
    @classmethod
    def parse(cls, version_str: str):
        parts = version_str.split('.')
        if len(parts) < 2 or len(parts) > 4:
            raise ValueError("Invalid version string format")
        
        try:
            parts = [int(p) for p in parts]
        except ValueError:
            raise ValueError("Version components must be integers")
        
        for p in parts:
            if p < 0:
                raise ValueError("Version components cannot be negative")
        
        if len(parts) == 2:
            return cls(parts[0], parts[1])
        elif len(parts) == 3:
            return cls(parts[0], parts[1], parts[2])
        else:
            return cls(parts[0], parts[1], parts[2], parts[3])
        
    
    @property
    def major(self) -> str: return f"{self._major}"
    
    @major.setter
    def major(self, value: int):
        if value >= 0:
            self._major = value
        else:
            raise ValueError("Основная версия должна быть положительной")
    

    @property
    def minor(self) -> str: return f"{self._minor}"
    
    @minor.setter
    def minor(self, value: int):
        if value >= 0:
            self._minor = value
        else:
            raise ValueError("Второстепенная версия должна быть положительной")
    

    @property
    def build(self) -> str: return f"{self._build}"
    
    @build.setter
    def build(self, value: int):
        if value >= 0:
            self._build = value
        else:
            raise ValueError("Версия сборки должна быть положительной")
        

    @property
    def revision(self) -> str: return f"{self._revision}"
    
    @revision.setter
    def revision(self, value: int):
        if value >= 0:
            self._revision = value
        else:
            raise ValueError("Версия сборки должна быть положительной")
        
    
    def __str__(self):
        if self._build == -1:
            return f"{self._major}.{self._minor}"
        elif self._revision == -1:
            return f"{self._major}.{self._minor}.{self._build}"
        else:
            return f"{self._major}.{self._minor}.{self._build}.{self._revision}"
        
    @property
    def ToString(self):
        if self._build == -1:
            return f"{self._major}.{self._minor}"
        elif self._revision == -1:
            return f"{self._major}.{self._minor}.{self._build}"
        else:
            return f"{self._major}.{self._minor}.{self._build}.{self._revision}"
    

    def __eq__(self, other):
        if not isinstance(other, Version):
            return False
        return (self._major == other._major and 
                self._minor == other._minor and 
                self._build == other._build and 
                self._revision == other._revision)
    

    def __lt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        if self._major != other._major:
            return self._major < other._major
        if self._minor != other._minor:
            return self._minor < other._minor
        if self._build != other._build:
            return self._build < other._build
        return self._revision < other._revision
    

    