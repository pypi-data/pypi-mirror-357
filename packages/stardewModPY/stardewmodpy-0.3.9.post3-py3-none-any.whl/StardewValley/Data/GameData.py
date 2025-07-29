from .model import modelsData
from typing import Optional

class Season:
    def __init__(self, lower: bool = False):
        self.lower = lower
        self_outer = self

        seasons = ["Spring", "Summer", "Fall", "Winter"]

        for season_name in seasons:
            def make_init(self_outer):
                return lambda self: setattr(self, "_outer", self_outer)

            def make_getJson(season_name):
                return lambda self: season_name.lower() if self._outer.lower else season_name

            cls = type(
                season_name,
                (object,),
                {
                    "__init__": make_init(self_outer),
                    "getJson": make_getJson(season_name),
                    "__repr__": lambda self, name=season_name: f"<{name}>"
                }
            )

            setattr(self, season_name, cls())





class AquariumType(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "eel"
    
    class Eel(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "eel"
    
    class Cephalopod(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "cephalopod"
    
    class Crawl(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "crawl"
    
    class Ground(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "ground"
    
    class Fish(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "fish"
    
    class Front_crawl(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "front_crawl"

class MusicContext(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "Default"

    class Default(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "Default"

    class SubLocation(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "SubLocation"
           
class AudioCategory(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "Default"
    
    class Default(modelsData):
        def __init__(self):
            pass
        def getJson(self) -> str:
            return "Default"
    
    class Music(modelsData):
        def __init__(self):
            pass
        def getJson(self) -> str:
            return "Music"
    
    class Sound(modelsData):
        def __init__(self):
            pass
        def getJson(self) -> str:
            return "Sound"
    
    class Ambient(modelsData):
        def __init__(self):
            pass
        def getJson(self) -> str:
            return "Ambient"
    
    class Footsteps(modelsData):
        def __init__(self):
            pass
        def getJson(self) -> str:
            return "Footsteps"

class BCFragility(modelsData):
    def __init__(self, fragility:int):
        if fragility < 0 or fragility > 2:
            raise ValueError("The possible values are 0 (pick up with any tool), 1 (destroyed if hit with an axe/hoe/pickaxe, or picked up with any other tool), or 2 (can't be removed once placed). Default 0.")
        self.fragility = fragility

    def getJson(self) -> int:
        return self.fragility
    

class StackSizeVisibility(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "Show"

    class Hide(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "Hide"
    
    class Show(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "Show"
    
    class ShowIfMultiple(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "ShowIfMultiple"

class Quality(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> int:
        return 0
    
    class Normal(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 0
    
    class Silver(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 1
    
    class Gold(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 2
    
    class Iridium(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 3

class QuantityModifiers(modelsData):
    def __init__(
        self,
        *,
        Id:str,
        Condition: Optional[str] = None,
        Amount: Optional[float] = None,
        RandomAmount: Optional[list[float]] = None
    ):
        self.Id = Id
        self.Condition = Condition
        self.Amount = Amount
        self.RandomAmount = RandomAmount

class QualityModifierMode(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "Stack"

    class Stack(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "Stack"
    
    class Minimum(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "Minimum"
    
    class Maximum(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "Maximum"

class ToolUpgradeLevel(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> int:
        return 0

    class Normal(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 0
    
    class Copper(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 1
    
    class Steel(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 2
    
    class Gold(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 3
    
    class IridiumTool(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 4
    
    class Bamboo(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 0
    
    class Training(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 1
    
    class Fiberglass(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 2
    
    class IridiumRod(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 3
    
    class AdvancedIridiumRod(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 4

class Modification(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "Multiply"
    
    class Multiply(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Multiply"
    
    class Add(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Add"
    
    class Subtract(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Subtract"
    
    class Divide(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Divide"
    
    class Set(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Set"

class AvailableStockLimit(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "None"
    
    class none(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "None"
    
    class Player(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Player"
    
    class Global(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Global"

class Gender(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "Undefined"
    
    class Male(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Male"
    
    class Female(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Female"
    
    class Undefined(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Undefined"

class Age(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "Adult"
    
    class Adult(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Adult"
    class Teen(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Teen"
    
    

class Social(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "Neutral"
    
    class Neutral(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Neutral"
    
class Manner(Social):
    def __init__(self):
        super().__init__()
    
    class Polite(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Polite"
    
    class Rude(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Rude"

class SocialAnxiety(Social):
    def __init__(self):
        super().__init__()
    
    class Outgoing(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Outgoing"
    
    class Shy(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Shy"

class Optimism(Social):
    def __init__(self):
        super().__init__()
    
    class Negative(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Negative"
    
    class Positive(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Positive"


class HomeRegion(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "Other"
    
    class Town(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Town"
    
    class Desert(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Desert"

    class Other(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Other"


class Calendar(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "AlwaysShown"
    
    
    
    class HiddenAlways(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "HiddenAlways"
    
    class HiddenUntilMet(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "HiddenUntilMet"
    
    class AlwaysShown(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "AlwaysShown"
        

class SocialTab(Calendar):
    def __init__(self):
        super().__init__()
    
    class UnknownUntilMet(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "UnknownUntilMet"
    
class EndSlideShow(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "MainGroup"
    
    class Hidden(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Hidden"
        
    class MainGroup(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "MainGroup"
    

    class TrailingGroup(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "TrailingGroup"
    

class ItemSpawnFields(modelsData):
    def __init__(
        self,
        Id: str=None,
        ItemId: str=None,
        RandomItemId: Optional[list[str]]=None,
        Condition: Optional[str]=None,
        PerItemCondition: Optional[str]=None,
        MaxItems: Optional[int]=None,
        IsRecipe: Optional[bool]=None,
        Quality: Optional[int]=None,
        MinStack: Optional[int]=None,
        MaxStack: Optional[int]=None,
        ObjectInternalName: Optional[str]=None,
        ObjectDisplayName: Optional[str]=None,
        ObjectColor: Optional[str]=None,
        ToolUpgradeLevel: Optional[int]=None,
        QualityModifiers: Optional[list[QuantityModifiers]]=None,
        StackModifiers: Optional[list[QuantityModifiers]]=None,
        QualityModifierMode: Optional[str]=None,
        StackModifierMode: Optional[str]=None,
        ModData: Optional[dict[str,str]]=None
    ):
        self.Condition = Condition
        self.Id = Id
        self.ItemId = ItemId
        self.RandomItemId = RandomItemId
        self.MaxItems = MaxItems
        self.MinStack = MinStack
        self.MaxStack = MaxStack
        self.Quality = Quality
        self.ObjectInternalName = ObjectInternalName
        self.ObjectDisplayName = ObjectDisplayName
        self.ObjectColor = ObjectColor
        self.ToolUpgradeLevel = ToolUpgradeLevel
        self.IsRecipe = IsRecipe
        self.StackModifiers = StackModifiers
        self.StackModifierMode = StackModifierMode
        self.QualityModifiers = QualityModifiers
        self.QualityModifierMode = QualityModifierMode
        self.ModData = ModData
        self.PerItemCondition = PerItemCondition

class CommonFields(modelsData):
    def __init__(
        self,
        CommonFields: ItemSpawnFields=None
    ):
        self.CommonFields = CommonFields
    
    def getJson(self, useGetStr:Optional[list[str]]=None, ignore: Optional[list[str]]=None) -> dict: #customized because of getStr functions
        ignore_finish = ["CommonFields"]
        if ignore is not None:
            ignore_finish.extend(ignore)

        json = self.CommonFields.getJson()
        json.update(super().getJson(useGetStr=useGetStr,ignore=ignore_finish))
        return json