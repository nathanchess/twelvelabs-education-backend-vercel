from abc import ABC, abstractmethod

class LLMProvider(ABC):

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass
    
    @abstractmethod
    def generate_chapters(self):
        pass
    
    @abstractmethod
    def generate_key_takeaways(self):
        pass
    
    @abstractmethod
    def generate_pacing_recommendations(self):
        pass

    @abstractmethod
    def generate_quiz_questions(self):
        pass
    
    @abstractmethod
    def generate_engagement(self):
        pass
    
    @abstractmethod
    def generate_gist(self):
        pass