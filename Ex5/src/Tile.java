import java.awt.Color;
import java.awt.Font;
import java.awt.FontMetrics;
import java.awt.Graphics;

// Class for one tile on the board
class Tile {
    private int value;          //value of tile
    private int size = 75;      //size of tile (constant)
    private int margin = 16;    //margin of tile (constant)
    
    // Constructor with default 0 value
    public Tile() {
        value = 0;
    }
    
    // Constructor with specific value
    public Tile(int n) {
        value = n;
    }
    
    // Method for getting value of tile
    public int getValue() {
        return value;
    }

    // Method for setting value of tile
    public void setValue(int value) {
        this.value = value;
    }

    // Method for checking if tile is empty
    public boolean isEmpty() {
        return value == 0;
    }
    
    // Method for double value of tile
    public void doubleValue() {
        this.value *= 2;
    }
    
    // Method for checking if tiles has same value
    public boolean isSame(Tile t) {
        return this.value == t. value ? true : false;
    }
    
    // Method for drawing the tile
    public void draw(Graphics g, int x, int y) {
        int xCoord = x * (margin + size) + margin;
        int yCoord = y * (margin + size) + margin;
        
        g.setColor(getColTile());
        g.fillRoundRect(xCoord, yCoord, size, size, 33, 33);
        g.setColor(getColVal());
        Font font = new Font("Arial", Font.BOLD, 24);
        g.setFont(font);
        FontMetrics fm = g.getFontMetrics(font);
        String s = String.valueOf(value);

        int w = fm.stringWidth(s); 
        int h = -(int) fm.getLineMetrics(s, g).getBaselineOffsets()[2];

        if (value != 0)
          g.drawString(s, xCoord + (size-w)/2, yCoord + size-(size-h)/2 - 2);
    }

    // Method for setting color of tile value 
    public Color getColVal() {
        if (value < 16)
            return new Color(0x776e65);
        else
            return new Color(0xf9f6f2);
    }

    // Method for setting tile color
    public Color getColTile() {
        switch (value) {
            case 2:
                return new Color(0xeee4da);
            case 4:
                return new Color(0xede0c8);
            case 8:
                return new Color(0xf2b179);
            case 16:
                return new Color(0xf59563);
            case 32:
                return new Color(0xf67c5f);
            case 64:
                return new Color(0xf65e3b);
            case 128:
                return new Color(0xedcf72);
            case 256:
                return new Color(0xedcc61);
            case 512:
                return new Color(0xedc850);
            case 1024:
                return new Color(0xedc53f);
            case 2048:
                return new Color(0xedc22e);
            case 4096: case 8192:
                return new Color(0,0,0);
            default:
                return new Color(0xcdc1b4);
        }
    }
}
