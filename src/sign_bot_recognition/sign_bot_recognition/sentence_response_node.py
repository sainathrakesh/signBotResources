import os
import re
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import subprocess

class SentenceResponseNode(Node):
    def __init__(self):
        super().__init__('sentence_response_node')
        self.get_logger().info("Sentence Response Node started!")

        self.subscription = self.create_subscription(
            String,
            '/finalized_sentence',
            self.handle_sentence,
            10
        )
        self.questions_and_answers = {
        "du selbst vorstellen": "humanoid_intro",
        "sie machen was": "ich-computer-arbeiten",
        "sie batterie einstecken": "ja-ich-sie-einstecken",
        "sie wer": "ich-4ne1",
        "sie fabrik arbeiten": "ja-ich-fabrik-arbeiten",
        "sie batterie pruefen": "ja-ich-batterie-prufen",
        "sie messen müssen": "nein-danke", #pending
        "roboter reinigen": "ja-roboter-reinigen",
        "sie ich helfen koonnen": "ja-gerne",
        "sie industrie arbeiten": "ja-ich-industrie-arbeiten",
        "sie automobile mögen": "ja-ich-automobile-mogen", #pending
        "polizei kommen": "ja-das-polizei", #pending
        "wir abmachen können": "ja-einverstanden", #pending
        "sie medizin brauchen": "nein-danke", 
        "sie fertig": "ja-ich-fertig"
    }



        self.response_script_dir = "/home/pepper/sign_bot_neura_challenge/src/sign_bot_mimic/sign_bot_mimic"

    def normalize(self, text):
        text = text.lower().strip()
        text = re.sub(r'[^\wäöüß\s]', '', text)  # remove punctuation but keep German letters
        return text

    def handle_sentence(self, msg):
        raw_input = msg.data
        sentence = self.normalize(raw_input)
        self.get_logger().info(f"Raw received: {repr(raw_input)}")
        self.get_logger().info(f"Normalized sentence: {sentence}")

        response = None
        for question, answer in self.questions_and_answers.items():
            self.get_logger().info(f"Checking if '{question}' in '{sentence}'")
            if question in sentence:
                response = answer
                break

        if response:
            self.get_logger().info(f"Matched response: {response}")
            script_name = self.slugify(response) + ".py"
            script_path = os.path.join(self.response_script_dir, script_name)

            if os.path.exists(script_path):
                self.get_logger().info(f"Launching response script: {script_name}")
                try:
                    subprocess.Popen(['python3', script_path])
                except Exception as e:
                    self.get_logger().error(f"Failed to run script: {e}")
            else:
                self.get_logger().warn(f"Script not found: {script_path}")
        else:
            self.get_logger().warn("No matching response found.")

    def slugify(self, text):
        return text.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue") \
            .replace("ß", "ss").replace(",", "").replace(".", "").replace("!", "").replace("?", "") \
            .replace(" ", "_")

def main(args=None):
    rclpy.init(args=args)
    node = SentenceResponseNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

