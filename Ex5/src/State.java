import java.util.ArrayList;
import java.util.List;

// Class for regular state in game
public class State {
    public Tile[] board;    //array of the board tiles
    public int points;      //score of the state
    public boolean lost;    //attribute for lost

    // Constructor with default values
    State() {
        this.points = 0;
        this.lost = false;
        this.board = new Tile[16];
        for (int i = 0; i < board.length; i++)
            board[i] = new Tile();
    }

    // Constructor with specific values
    State(int p, boolean l, Tile[]b) {
        this.points = p;
        this.lost = l;
        this.board = new Tile[16];
        for (int i = 0; i < board.length; i++)
            board[i] = new Tile(b[i].getValue());
    }

    // Method for cloning state
    public State clone() {
        return new State(this.points, this.lost, this.board);
    }

    // Method for checking difference in states
    public boolean isDiff(State old) {
        for (int i = 0; i < 16; i++)
            if (!this.board[i].isSame(old.board[i]))
                return true;
        return false;
    }

    // Method for one move, change of state
    public void move (String dir) {
        moveLines(dir);
        switch (dir) {
        case "up":
            for (int r = 0; r < 3; r++)
                mergeRows(r,r+1);
            break;
        case "down":
            for (int r = 3; r > 0; r--)
                mergeRows(r,r-1);
            break;
        case "right":
            for (int c = 3; c > 0; c--)
                mergeCols(c,c-1);
            break;
        case "left":
            for (int c = 0; c < 3; c++)
                mergeCols(c,c+1);
            break;
        }
        moveLines(dir); 
    }

    // Method for merging two rows
    public void mergeRows(int first, int second) {
        for (int i = 0; i < 4; i++)
            if (board[i+first*4].isSame(board[i+second*4])) {
                board[i+first*4].doubleValue();
                board[i+second*4].setValue(0);
                points += board[i+first*4].getValue();
            }
    }

    // Method for merging two columns
    public void mergeCols(int first, int second) {
        for (int i = 0; i < 16; i += 4 )
            if (board[i+first].isSame(board[i+second])) {
                board[i+first].doubleValue();
                board[i+second].setValue(0);
                points += board[i+first].getValue();
            }
    }

    // Method for shrinking line in specific direction
    public List<Integer> shrinkLine(int index, String dir) {
        List<Integer> newLine = new ArrayList<Integer>(4);
        int i;
        if (dir == "left" || dir == "right")
            for (i = 0; i < 4; i++)
                if (!board[i+index*4].isEmpty())
                    newLine.add(board[i+index*4].getValue());
        if (dir == "up" || dir == "down")
            for (i = 0; i < 16; i += 4)
                if (!board[i+index].isEmpty())
                    newLine.add(board[i+index].getValue());
        
        while (newLine.size() != 4) {
            if (dir == "left" || dir == "up")
                newLine.add(0);
            else if (dir == "right" || dir == "down")
                newLine.add(0,0);
        }
        return newLine;
    }

    // Method for moving all lines in specific direction
    public void moveLines(String dir) {
        for (int r = 0; r < 4; r++) {
            List<Integer> shrinked = shrinkLine(r,dir);
            for (int c = 0; c < 4; c++) {
                if (dir == "left" || dir == "right")
                    board[c+r*4].setValue(shrinked.get(c));
                else if (dir == "up" || dir == "down")
                    board[r+c*4].setValue(shrinked.get(c));
            }
        }
    }

    // Method for adding random new tile (0.9/0.1)
    public void addNew() {
        List<Tile> available = getAvailable();
        if (!available.isEmpty()) {
            int i = (int) (Math.random() * available.size()) % available.size();
            available.get(i).setValue(Math.random() < 0.9 ? 2 : 4);
        }
    }

    // Method for collecting all empty tiles
    public List<Tile> getAvailable(){
        List<Tile> availableTiles = new ArrayList<Tile>();
        for (int i = 0; i < board.length; i++)
            if (board[i].isEmpty())
                availableTiles.add(board[i]);
        return availableTiles;
    }

    // Method which checks if state is movable
    public boolean movable() {
        if (getAvailable().size() != 0)
            return true;
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                if ((c < 3 && board[c+r*4].isSame(board[(c+1)+r*4])) ||
                        (r < 3 && board[c+r*4].isSame(board[c+(r+1)*4])))
                    return true;
        return false;
    }

    // Method for printing the state
    public void print() {
        for (int i = 0; i < board.length; i++)
            if (i % 4 == 3)
                System.out.println(board[i].getValue());
            else
                System.out.print(board[i].getValue()+",");
    }

    // Method for counting specific gradient of state
    public int grade(int[]g){
        int G = 0;
        for (int i = 0; i < board.length; i++)
            G += board[i].getValue() * g[i];
        return G;
    }

    // Method for counting and maximizing 4 main gradients
    public int gradient() {
        int grad1[] = {3,2,1,0,2,1,0,-1,1,0,-1,-2,0,-1,-2,-3}; //up-right
        int grad2[] = {0,1,2,3,-1,0,1,2,-2,-1,0,1,-3,-2,-1,0}; //up-left
        int grad3[] = {0,-1,-2,-3,1,0,-1,-2,2,1,0,-1,3,2,1,0}; //down-left
        int grad4[] = {-3,-2,-1,0,-2,-1,0,1,-1,0,1,2,0,1,2,3}; //down-right
    
        int G1,G2,G3,G4;
    
        G1 = grade(grad1);
        G2 = grade(grad2);
        G3 = grade(grad3);
        G4 = grade(grad4);
    
        return (Math.max(Math.max(G1, G2), Math.max(G3, G4)));
    }

    // Method for searching max value of state
    public int max() {
        int max = 0;
        for (int i = 0; i < board.length; i++)
            if (!board[i].isEmpty())
                if (board[i].getValue() > max)
                    max = board[i].getValue();
        return max;
    }

}
