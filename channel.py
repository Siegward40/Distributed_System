class Channel:
    def __init__(self, process_sender, process_receiver):
        print("Création d'un channel entre le process {} et le process {}".format(process_sender.name_process, process_receiver.name_process))
        self.process_sender = process_sender
        self.process_receiver = process_receiver
        self.message = None

    def send_message(self):
        if self.process_receiver.state is None:
            print(f"Channel {self.name} (ID: {self.id}) ne peut pas envoyer le message, le process destinataire est arrêté.")
        else:
            self.message = self.process_sender.get_message()
            self.process_receiver.receive_message(self.message)
            print(f"Channel envoie le message du process {self.process_sender.name_process} au process {self.process_receiver.name_process}.")

    def receive_message(self, message):
        print(f"Channel entre {self.process_sender.name_process} et {self.process_receiver.name_process} a reçu le message: {message}")
    
