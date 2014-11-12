import java.awt.AWTException;
import java.awt.Color;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.Robot;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.util.HashMap;
import java.util.Map;
import javax.swing.JPanel;

// Class for the maintenance 2048 game
@SuppressWarnings("serial")
public class Game_2048 extends JPanel{
    private State game;     //actual state of game
    private boolean auto;   //attribute for auto-run

    // Constructor where key listener is installed 
    // for basic events and classic play
    // Also generator of key events for auto-run
    public Game_2048(){
        setFocusable(true);
        addKeyListener(new KeyAdapter() {
            @Override
            public void keyPressed(KeyEvent e) {
                // basic operations
                if (e.getKeyCode() == KeyEvent.VK_ESCAPE || e.getKeyCode() == KeyEvent.VK_Q)
                    System.exit(0);
                else if (e.getKeyCode() == KeyEvent.VK_N)
                    start();
                // classic part for one move
                State old = game.clone();
                if (!game.lost) {
                    switch (e.getKeyCode()) {
                    case KeyEvent.VK_UP:
                        game.move("up");
                        break;
                    case KeyEvent.VK_RIGHT:
                        game.move("right");
                        break;
                    case KeyEvent.VK_DOWN:
                        game.move("down");
                        break;
                    case KeyEvent.VK_LEFT:
                        game.move("left");
                        break;
                    case KeyEvent.VK_A:
                        auto = auto ? false : true;
                        break;
                    default:
                        break;
                    }
                }
                if (game.isDiff(old))
                    game.addNew();
                
                if (!game.movable()) {
                    game.lost = true;
                    auto = false;
                }
                repaint(); // draw actual state
                // autorun part - fire new key event for best move
                if (auto) {
                    try {
                        Robot robot;
                        Thread.sleep(0);
                        robot = new Robot();
                        robot.keyPress(findBest(game, 6));
                    } catch (AWTException | InterruptedException e1) {
                        e1.printStackTrace();
                    }
                }
            }
        });
        start(); //first start  
    }
    
    // Method for start and restart initialization
    public void start() {
        game = new State();
        auto = false;
        game.addNew();
    }
    
    // Method where best move search is started
    public int findBest(State root, int depth) {
        switch ((String)player(root, depth).get("Direction")) { // return value translated to ke event
        case "up":
            return KeyEvent.VK_UP;
        case "down":
            return KeyEvent.VK_DOWN; 
        case "left":
            return KeyEvent.VK_LEFT;
        case "right":
            return KeyEvent.VK_RIGHT;
        }
        return -1;
    }
    
    // Implementation of expectimax - player part
    public Map<String, Object> player(State s, int depth) {
        String [] directions = {"up","down","left","right"};
        Map<String, Object> move = new HashMap<>();
        String best_move = "no move";
        double eval = -1;
        // stop and eval constraints
        if (!s.movable())
            eval = -1;
        else if (depth == 0) {
            if (s.movable())
                eval = s.gradient();
            else
                eval = -1;
        }
        else { // max nodes (directions)
            eval = -1;
             for (String dir : directions) {
                 State next = s.clone();
                 next.move(dir);
                 
                 if (!next.isDiff(s))
                     continue;

                 double score = computer(next, depth - 1);
                 if (score >= eval){
                        eval = score;
                        best_move = dir;
                    }
             }
        }
        
        move.put("Points", eval);
        move.put("Direction", best_move);
                
        return move;
    }
    
    // Implementation of expectimax - computer part
    public double computer(State s, int depth) {
        double score = 0;
        double weight = 0;
        double prob;
        // expectation with probablities (new tiles)
        for (int i = 0; i < s.getAvailable().size(); i++) { 
            for (int j = 2; j <= 4; j+=2) {
                State next = s.clone();
                next.getAvailable().get(i).setValue(j);
                Map<String, Object> actual = player(next, depth-1);
                if (j == 4)
                    prob = 0.1;
                else 
                    prob = 0.9;
                    
                score += ((Double)actual.get("Points")).intValue() * prob;
                weight += prob;
            }
        }     
        return score/weight;
    }
    
    // Evaluation method with call for heuristic
    public int heureka(State s) {
        return s.gradient();
    }
    
    // Method for drawing the game
    @Override
    public void paint(Graphics g) {
        // main window
        super.paint(g);
        Graphics2D window = ((Graphics2D) g);
        window.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        window.setRenderingHint(RenderingHints.KEY_STROKE_CONTROL, RenderingHints.VALUE_STROKE_NORMALIZE);
        window.setColor(new Color(0xbbada0));
        window.fillRect(0, 0, getSize().width, getSize().height);
        // all tiles
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                game.board[c+r*4].draw(window, c, r);
        // score and instructions print
        window.setColor(new Color(0, 0, 0));
        window.setFont(new Font("Arial", Font.PLAIN, 16));
        window.drawString("N: new game  |  Q: quit  |  Points: " + game.points, 50, 395);
        window.drawString("A: auto-run (expectimax+gradient)", 75, 420);
        if (game.lost) {
            window.drawString("2048: not achieved", 115, 445);
            window.setColor(new Color(255, 255, 255, 90));
            window.fillRect(0, 0, getWidth(), getHeight());
            window.setColor(new Color(0, 0, 0));
            window.setFont(new Font("Arial", Font.BOLD, 48));
            window.drawString("Game over!", 68, 200);
            window.drawString("MAX: "+game.max(), 68, 250);
        }
        else if (game.max() >= 2048)
            window.drawString("2048: achieved", 140, 445);
        else
            window.drawString("2048: - - -", 140, 445);
    }
    
    // Not in use
    // Implementation of minimax with alpha-beta prunning
    public Map<String, Object> alphabeta(State s, int depth, int alpha, int beta, boolean max) {
        String [] directions = {"up","down","left","right"};
        Map<String, Object> move = new HashMap<>();
        String dir = "";
        int eval = 0;
        // stop and eval constraints
        if (s.lost)
            eval = 0;
        else if (depth == 0)
            eval = heureka(s);
        else { // max node part (directions)
            if(max) {
                for (String d : directions) {
                    State next = s.clone();
                    next.move(d);
                    
                    if (!next.isDiff(s))
                        continue;
                        
                    Map<String, Object> actual = alphabeta(next, depth-1, alpha, beta, false);
                                        
                    if (((Integer)actual.get("Points")).intValue() > alpha) {
                        alpha = ((Integer)actual.get("Points")).intValue();
                        dir = d;
                    }
                    if (beta <= alpha)
                        break;
                }
                eval = alpha;
            }
            else { // min node part (new tiles)
                wanted: for (int i = 0; i < s.getAvailable().size(); i++) {
                    for (int j = 2; j <= 4; j+=2) {
                        State next = s.clone();
                        next.getAvailable().get(i).setValue(j);

                        Map<String, Object> actual = alphabeta(next, depth-1, alpha, beta, true);
                        
                        if (((Integer)actual.get("Points")).intValue() < beta)
                            beta = ((Integer)actual.get("Points")).intValue();
                        
                        if (beta <= alpha)
                            break wanted;
                    }
                }
                eval = beta;
            }
        }
        move.put("Points", eval);
        move.put("Direction", dir);
        
        return move;
    }
}
