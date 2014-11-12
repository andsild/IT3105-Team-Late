import javax.swing.JFrame;
import javax.swing.WindowConstants;

// Main method for launching Game_2048
public class Main{
    public static void main(String[] args) {
        JFrame game = new JFrame();
        game.setTitle("2048 - Expectimax with gradient eval");
        game.setSize(380, 480);
        game.setLocationRelativeTo(null);
        game.setResizable(false);
        game.setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE);
        game.add(new Game_2048());
        game.setVisible(true);
    }
}
