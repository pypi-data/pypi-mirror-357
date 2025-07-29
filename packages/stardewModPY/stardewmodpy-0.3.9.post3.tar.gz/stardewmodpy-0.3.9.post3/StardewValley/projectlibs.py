import os, re
class colorize:
    def __init__(self):
        self.black=30
        self.red=31
        self.green=32
        self.yellow=33
        self.blue=34
        self.magenta=35
        self.cyan=36
        self.white=37
    
    def colorize(self, color:int):
        return f"\033[{color}m"
    def reset(self):
        return "\033[0m"

class libModel:
    def __init__(self, optionals: dict, modName: str):
        self.optionals=optionals
        self.modName=modName
        self.imports=""
        self.implements=""
        self.classData=""

        self.classFileData=""
        self.classFileData_imports=""
        self.classFileData_Father=""
        self.classFileData_params=""
        self.classFileData_contents=""

        self.import_file="__init__.py"

        self.corrects={
            "Maps":"Maps",
            "NPCS":"NPCs",
            "Dialogues":"Dialogues",
            "Events":"Events",
            "Schedules":"Schedules"
        }
        
    def write_file(self, path, content):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    def contents(self):
        if self.optionals[self.corrects[self.__class__.__name__]]:
            os.makedirs(os.path.join(self.modName, self.__class__.__name__))
            self.write_file(os.path.join(self.modName, self.__class__.__name__, self.import_file), self.classData)
    
    

    

    def add_item(self, item_name: str):
        function_name = self.corrects[self.__class__.__name__]
        file_path = os.path.join(self.modName, "ModEntry.py")

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        new_lines = []
        inside_function = False
        inside_list = False
        indent = ""
        added = False

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Detecta o começo da chamada multilinha, ex: NPCs(
            if stripped.startswith(f"{function_name}("):
                inside_function = True
                new_lines.append(line)
                continue

            if inside_function:
                # Procura pela linha que inicia a lista, ex: NPCs_List=[
                if stripped.startswith(f"{function_name}_List=["):
                    inside_list = True
                    indent = line[:line.find(stripped)]
                    new_lines.append(line)
                    continue

                # Se estiver dentro da lista, procura a linha que fecha a lista ']'
                if inside_list:
                    if stripped.startswith("]"):
                        already_exists = False
                        for l in new_lines:
                            if f"{function_name}_List.{item_name}()" in l:
                                already_exists = True
                                break
                        if not already_exists:

                            if new_lines:
                                last_line = new_lines[-1].rstrip()
                                if not last_line.endswith(","):
                                    new_lines[-1] = new_lines[-1].rstrip() + ",\n"
                            new_lines.append(f"{indent}    {function_name}_List.{item_name}(),\n")
                            added = True
                        else:
                            print(f"⚠️ Item {item_name} já está presente em {function_name}_List, não adicionando.")
                        new_lines.append(line)
                        inside_list = False
                        inside_function = False
                        continue
                    else:
                        new_lines.append(line)
                        continue

                # Se encontrou fechamento da função depois da lista
                if stripped.startswith(")"):
                    inside_function = False
                    new_lines.append(line)
                    continue

                new_lines.append(line)
                continue

            new_lines.append(line)

        if not inside_function and not inside_list:
            if added:
                print(f"✅ Item {item_name} adicionado em {function_name} -> {function_name}_List")
            else:
                print(f"⚠️ Nenhuma alteração realizada, item {item_name} já existia em {function_name}_List")
        else:
            print(f"❌ Not found: {function_name}(mod=self, {function_name}_List=[])")

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

        if added:
            self.add_import(item_name)




    def add_import(self, name:str):
        importFile=os.path.join(self.modName, self.__class__.__name__, self.import_file)
        with open(importFile, 'a', encoding='utf-8') as f:
            f.write(f"\nfrom NPCS.{name} import {name}\n")

        newFile=os.path.join(self.modName, self.__class__.__name__, name+".py")
        self.buildClassData(name)
        with open(newFile, 'w', encoding='utf-8') as f:
            f.write(self.classFileData)
    
    def buildClassData(self, name):
        self.classFileData=f"""{self.classFileData_imports}

class {name}{self.classFileData_Father}:
    def __init__(self{self.classFileData_params}):
        {self.classFileData_contents.replace("###name###", name)}"""


class Maps(libModel):
    def __init__(self, optionals: dict, modName: str):
        super().__init__(optionals, modName)
        self.imports="from Maps.Maps import Maps" if self.optionals["Maps"] else ""
        
        self.implements="Maps(self)" if self.optionals["Maps"] else ""

        self.classData=f"""from StardewValley.Data.SVModels import Maps as MapsModel
from StardewValley import Helper

class Maps(MapsModel):
    def __init__(self, mod: Helper):
        super().__init__(mod)
        self.mod.assetsFileIgnore=[]
    
    def contents(self):
        super().contents()

"""
        self.import_file="Maps.py"
    
    
    
class NPCS(libModel):
    def __init__(self, optionals, modName):
        super().__init__(optionals, modName)

        self.imports="""import NPCS as NPCs_List
from StardewValley.Data.SVModels.NPCs import NPCs
"""
        
        self.implements="NPCs(mod=self, NPCs_List=[])" if self.optionals["NPCs"] else ""

        self.classFileData_imports="""from StardewValley.Data import CharactersData, Home, Gender, Age, Manner, SocialAnxiety, Optimism, Season
from StardewValley.Data.XNA import Position
"""
        self.classFileData_Father="(CharactersData)"
        self.classFileData_contents="""self.key=###name###
        self.DisplayName=###name###
        self.Gender=Gender.Undefined
        self.Age=Age.Adult
        self.Manner=Manner.Neutral
        #self.SocialAnxiety=SocialAnxiety.Neutral
        self.Optimism=Optimism.Neutral
        self.BirthSeason=Season(lower=True).Spring
        self.BirthDay=1
        self.HomeRegion="Town"
        self.CanBeRomanced=False
        self.Home=[
            Home(
                Id="###name###House",
                Tile=Position(10, 10),
                Direction="right",
                Location="Town"
            ).getJson()
        ]"""
    

class Dialogues(libModel):
    def __init__(self, optionals, modName):
        super().__init__(optionals, modName)

        self.imports="""import Dialogues as Dialogues_List
from StardewValley.Data.SVModels.Dialogues import Dialogues
""" if self.optionals["Dialogues"] else ""

        self.implements="Dialogues(mod=self, Dialogues_List=[])" if self.optionals["Dialogues"] else ""


class Schedules(libModel):
    def __init__(self, optionals, modName):
        super().__init__(optionals, modName)

        self.imports="""import Schedules as Schedules_List
from StardewValley.Data.SVModels.Schedules import Schedules
""" if self.optionals["Schedules"] else ""

        self.implements="Schedules(mod=self, Schedules_List=[])" if self.optionals["Schedules"] else ""

class Events(libModel):
    def __init__(self, optionals, modName):
        super().__init__(optionals, modName)

        self.imports="""import Events as Events_list
from StardewValley.Data.SVModels.Events import Events
""" if self.optionals["Events"] else ""
        
        self.implements="Events(mod=self, Events_list=[])" if self.optionals["Events"] else ""


class ExtraContents:
    def __init__(self, optionals, modName):
        self.optionals=optionals
        self.modName=modName

        self.Dialogues=Dialogues(optionals, modName)
        self.Dialogues.contents()
        self.Maps=Maps(optionals, modName)
        self.Maps.contents()
        self.Events= Events(optionals, modName)
        self.Events.contents()
        self.NPCS=NPCS(optionals, modName)
        self.NPCS.contents()
        self.Schedules=Schedules(optionals, modName)
        self.Schedules.contents()

    
    def saveEntry(self):
        mod_entry_path = os.path.join(self.modName, "ModEntry.py")
        framework_content=""
        framework_content_import=""
        if self.optionals["framework"] is not None:
            framework_content=f", modFramework={self.optionals['framework']}(manifest=manifest)"
            framework_content_import=f", {self.optionals['framework']}"
        
        content = f"""from StardewValley import Manifest
from StardewValley.helper import Helper{framework_content_import}

{self.Maps.imports}

{self.NPCS.imports}

{self.Events.imports}

{self.Dialogues.imports}

{self.Schedules.imports}

class ModEntry(Helper):
    def __init__(self, manifest:Manifest):
        super().__init__(
            manifest=manifest{framework_content}
        )
        self.contents()
    
    def contents(self):
        # Add your contents here
        {self.Maps.implements}

        {self.NPCS.implements}

        {self.Events.implements}

        {self.Dialogues.implements}

        {self.Schedules.implements}

"""
        with open(mod_entry_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    def saveMain(self, author:str, version:str, description:str):
        main_path = os.path.join(self.modName, "main.py")
        mainContent=f"""from ModEntry import ModEntry
from StardewValley import Manifest

manifest=Manifest(
    Name="{self.modName}",
    Author="{author}",
    Version="{version}",
    Description="{description}",
    UniqueID="{author}.{self.modName}"
)
mod=ModEntry(manifest=manifest)

mod.write()
"""
        with open(main_path, "w", encoding="utf-8") as f:
            f.write(mainContent)