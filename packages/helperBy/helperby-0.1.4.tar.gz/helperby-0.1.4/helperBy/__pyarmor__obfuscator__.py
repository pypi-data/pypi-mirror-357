import os
import sys
import shutil
import subprocess
from tempfile import mkdtemp
from typing import Optional

class PyObfuscateBuilder:
    def __init__(self):
        self._check_dependencies()

    def _check_dependencies(self):
        """Проверяет наличие необходимых зависимостей"""
        try:
            subprocess.run(['pyarmor', '--version'], 
                         check=True, 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
            subprocess.run(['pyinstaller', '--version'], 
                         check=True, 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise ImportError("Требуются PyArmor и PyInstaller. Установите: pip install pyarmor pyinstaller")

    def obfuscate(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        max_obfuscation: bool = True
    ) -> str:
        """Обфускация Python-файла
        
        Args:
            input_path: Путь к исходному файлу
            output_path: Путь для сохранения (None = перезаписать исходный)
            max_obfuscation: Максимальный уровень защиты
            
        Returns:
            Путь к обфусцированному файлу
        """
        if output_path is None:
            output_path = input_path

        cmd = [
            'pyarmor',
            'obfuscate',
            '--recursive',
            '--output', output_path,
        ]

        if max_obfuscation:
            cmd.extend([
                '--mix-str',
                '--assert-call',
                '--assert-import',
                '--restrict', '1',
                '--enable-jit',
                '--obf-mod', '1',
                '--obf-code', '1',
            ])

        cmd.append(input_path)

        try:
            subprocess.run(cmd, check=True)
            return output_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Ошибка обфускации: {e}")

    def build(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        *,
        onefile: bool = True,
        console: bool = True,
        clean: bool = True,
        obfuscate_level: int = 2
    ) -> str:
        """Сборка Python-скрипта в EXE с обфускацией
        
        Args:
            input_file: Входной .py файл
            output_file: Выходной .exe файл (None = автоматическое имя)
            onefile: Собирать в один файл
            console: Отображать консоль
            clean: Удалять временные файлы
            obfuscate_level: Уровень обфускации (0-2)
            
        Returns:
            Путь к собранному EXE-файлу
        """
        if not os.path.isfile(input_file):
            raise FileNotFoundError(f"Файл не найден: {input_file}")

        if output_file is None:
            output_file = os.path.splitext(input_file)[0] + '.exe'

        temp_dir = mkdtemp(prefix='pyobfuscate_')
        try:
            # Шаг 1: Обфускация
            obf_file = os.path.join(temp_dir, os.path.basename(input_file))
            if obfuscate_level > 0:
                self.obfuscate(
                    input_file, 
                    obf_file,
                    max_obfuscation=(obfuscate_level == 2))
            else:
                shutil.copy(input_file, obf_file)

            # Шаг 2: Сборка EXE
            pyinstaller_cmd = [
                'pyinstaller',
                '--noconfirm',
                '--log-level', 'ERROR',
                '--workpath', os.path.join(temp_dir, 'build'),
                '--specpath', temp_dir,
                '--distpath', os.path.dirname(output_file) or '.',
                '--name', os.path.splitext(os.path.basename(output_file))[0],
            ]

            if onefile:
                pyinstaller_cmd.append('--onefile')
            if not console:
                pyinstaller_cmd.append('--windowed')

            pyinstaller_cmd.append(obf_file)

            subprocess.run(pyinstaller_cmd, check=True)
            
            # Возвращаем полный путь к EXE
            exe_path = os.path.join(
                os.path.dirname(output_file) or '.',
                os.path.splitext(os.path.basename(output_file))[0] + '.exe'
            )
            
            if not os.path.exists(exe_path):
                raise RuntimeError("Сборка не удалась: EXE не создан")
                
            return os.path.abspath(exe_path)

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Ошибка сборки: {e}")
        finally:
            if clean:
                shutil.rmtree(temp_dir, ignore_errors=True)

# Упрощенный интерфейс
def build(
    input_py: str,
    output_exe: Optional[str] = None,
    **kwargs
) -> str:
    """Упрощенная функция для сборки
    
    Пример:
        build("script.py", "app.exe", onefile=True)
    """
    return PyObfuscateBuilder().build(input_py, output_exe, **kwargs)