from app.repository.user_repository import UserRepository
from app.domain.entities import User, Chat, Message

class ChatService:
    def __init__(self, userRepository: UserRepository) -> None:
        self.user_repository = userRepository
        
    def start_chat(self, user_a_id: int, user_b_id:int, content:str):
        user_a = self.user_repository.find_by_id(user_a_id)
        user_b = self.user_repository.find_by_id(user_b_id)
        if not user_b or not user_a:
            # El usuario b no se encontro
            return
        if not user_b.is_active:
            # El usuario esta inactivo, se crea el mensaje y chat, se settea como no delivered y se guarda en base de datos
            return
        # Se crea el objeto chat
        # new_chat = Chat(user_a=user_a_id, user_b=user_b_id)