from app.repository.user_repository import UserRepository
from app.domain.entities import Chat
from flask_socketio import join_room
class ChatService:
    def __init__(self, userRepository: UserRepository) -> None:
        self.user_repository = userRepository
        
    def start_chat(self, user_a_id: str, user_b_id:str, first_msg:str):
        user_a = self.user_repository.find_by_id(user_a_id)
        user_b = self.user_repository.find_by_id(user_b_id)
        if not user_b or not user_a:
            # El usuario b no se encontro
            return
        # Se crean objetos de dominio
        new_chat = Chat(user_a=user_a_id, user_b=user_b_id)
        # Con el uuid creado del Chat, se crea un room
        join_room(new_chat.id)
        
        # Si el user2 tambien esta activo, se mete al room
        # if user_b.is_active:
        #     join_room(new_chat.id, sid=user_b.sid)
        #     self._send_msg(new_chat.id, user_a.sid, first_msg)

    # def _send_msg(self, room, sender, msg):
        