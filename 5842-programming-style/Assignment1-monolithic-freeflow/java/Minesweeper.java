import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.util.Scanner;

public class Minesweeper {

    public static void main(String[] args) {
        // declare chess-board property having dimension of n*m
        final String fileEndings = ".cfg";
        
        /** ALESSIO: Use the proper capitalization for variable names! */
        final String msgnotvalid = "The provided input is not valid!";
        final String msgwon = "You Won!";
        final String msglost = "You Lost!";
        final String msgnotenough = "Not enough inputs!";
        
        /** ALESSIO: What about maxRowSize? */
        final Integer maxColumnSize = 20;

        String message = "";
        String chessboard = "";
        Integer mineNumber = 0;
        // Integer openCellNumber = 0;
        Boolean gameOver = false;
        Integer rowNumber = 0;
        Integer colNumber = 0;
        // declare arrays below only after reading the file.
        // boolean[] flagged
        // bollean[] mined
        // boolean[] opened
        // int[] neightbourMineCount

        // And System.exit() is also the only way to specify the return value:
        // 1. read file
        // 1a. check if file name is valid

        // A possible violation of style, as substring are abstract methods.
        /** ALESSIO: Ok. */
        String fileFullName = args[0];
        String extension = fileFullName.toLowerCase().substring(fileFullName.length() - fileEndings.length());
        String fileName = fileFullName.substring(0, fileFullName.length() - fileEndings.length());
        // System.out.println("length: " + fileName.length());
        if (fileName.length() == 0 || !extension.equals(fileEndings)) {
            System.exit(2);
        }
        /** 
            ALESSIO: Since you call exit before, why not simply use a sequence of if-then-statement instead of nesting
            them?
        */
        // 1b. check if file exists
        else {
            try {
                File f = new File(fileFullName);
                if (!f.exists()) {
                    System.exit(1);
                } else if (f.isDirectory()) {
                    System.exit(2);
                } else {
                    // Possible violation of style, use Buffered Reader to read files and have IO
                    // exception.
                    /** ALESSIO: Ok */

                    /** 
                        ALESSIO: Why do you need a RandomAccessFile? that's not really necessary so 
                        I need to consider this a violation of the style! 
                        
                        What is this code about? To check if the file is empty was not enough to call 
                            File.size() == 0 ?
                    */
                    RandomAccessFile fileHandler = new RandomAccessFile(f, "r");

                    long fileLength = fileHandler.length() - 1;
                    if (fileLength < 0) {
                        fileHandler.close();
                        System.exit(2);
                    }
                    fileHandler.seek(fileLength);
                    byte readByte = fileHandler.readByte();
                    fileHandler.close();
                    if (!(readByte == 0xA)) {
                        System.exit(2);
                    }

                    chessboard = "";

                    // re read the file with while counting lines.
                    /** ALESSIO: This is not really smart, why reading the file twice when you could do it in one pass? */
                    Scanner myReader = new Scanner(f);
                    int tempColSize = 0;
                    while (myReader.hasNextLine()) {
                        String data = myReader.nextLine();
                        chessboard += data;
                        colNumber = data.length();
                        // 1c. check if every row have the same character.
                        if (rowNumber == 0) {
                            tempColSize = colNumber;
                            if (colNumber > maxColumnSize || colNumber < 1)
                                System.exit(2);
                        } else {
                            // 1d. check the length of each row.
                            if (tempColSize != colNumber || colNumber > maxColumnSize || colNumber < 1) {
                                System.exit(2);
                            }
                        }
                        rowNumber++;
                    }
                    myReader.close();


                    // 1e. check the length of total column & empty board.
                    if (rowNumber > maxColumnSize || rowNumber < 1 || chessboard.length() == 0) {
                        System.exit(2);
                    }
                    if (rowNumber == 1 && colNumber == 1) {
                        System.exit(2);
                    }
                    // 1f. check if all characters are * and .
                    /** ALESSIO: This is ok, but I cannot understand why you could not check this while reading each line */
                    for (int i = 0; i < chessboard.length(); i++) {
                        if (!(chessboard.charAt(i) == '*' || chessboard.charAt(i) == '.')) {
                            System.exit(2);
                        }
                    }
                }

            } catch (FileNotFoundException e) {
                System.exit(2);
            } catch (IOException e) {
                System.exit(2);
            }


            // 1g. put chessboard into arrays.
            /** ALESSIO: I cannot understand why not using a 2D array instead of a linear one... */
            // **************************************//
            boolean[] flagged = new boolean[chessboard.length()];
            boolean[] mined = new boolean[chessboard.length()];
            boolean[] opened = new boolean[chessboard.length()];
            int[] neighbourMineCount = new int[chessboard.length()];
            // **************************************//
            for (int i = 0; i < chessboard.length(); i++) {
                flagged[i] = false;
                opened[i] = false;
                mined[i] = (chessboard.charAt(i) == '*') ? true : false;
                if (chessboard.charAt(i) == '*')
                    mineNumber++;
            }
            // check number of mine.
            if (mineNumber == rowNumber * colNumber)
                System.exit(2);
            
            // 1h. calculate neightbourMineCount
            for (int i = 0; i < chessboard.length(); i++) {
                int minecount = 0;
                if (i % colNumber != 0) { // not left most column
                    if (i - colNumber - 1 > 0 && mined[i - colNumber - 1] == true)
                        minecount++;
                    if (mined[i - 1] == true)
                        minecount++;
                    if (i + colNumber - 1 < (rowNumber * colNumber) && mined[i + colNumber - 1] == true)
                        minecount++;
                }
                if (i - colNumber > 0 && mined[i - colNumber] == true)
                    minecount++;
                if (i + colNumber < (rowNumber * colNumber) && mined[i + colNumber] == true)
                    minecount++;
                if ((i + 1) % colNumber != 0) { // not right most column
                    if (i - colNumber + 1 > 0 && mined[i - colNumber + 1] == true)
                        minecount++;
                    if (mined[i + 1] == true)
                        minecount++;
                    if (i + colNumber + 1 < (rowNumber * colNumber) && mined[i + colNumber + 1] == true)
                        minecount++;
                }
                neighbourMineCount[i] = minecount;
            }


            Scanner sc = new Scanner(System.in);
            // 2. Draw Board + Process Result
            /** ALESSIO: This is inaccurate. While using whle true when you can have sc.hasNextLine() ?! */
            while (true) {
                // 2a. Draw Board
                // print top row
                System.out.print('┌');
                for (var col = 1; col < colNumber; col++) {
                    System.out.print("───┬");
                }
                System.out.println("───┐");

                // draw datarow + middle row
                for (var row = 1; row <= rowNumber; row++) {
                    // data row
                    System.out.print('│');
                    for (var col = 1; col <= colNumber; col++) {
                        var index = (row - 1) * colNumber + (col - 1);
                        System.out.print(" ");
                        // 2aI. print cell logic
                        if (flagged[index] == true)
                            System.out.print("¶");
                        else {
                            if (opened[index] == true && mined[index] == true)
                                System.out.print("*");
                            else if (opened[index] == true && neighbourMineCount[index] == 0)
                                System.out.print("▓");
                            else if (opened[index] == true && neighbourMineCount[index] > 0)
                                /** ALESSIO: Probably String.valueOf is unecessary */
                                System.out.print(String.valueOf(neighbourMineCount[index]));
                            else if (opened[index] == false)
                                System.out.print(" ");
                        }
                        System.out.print(" ");
                        System.out.print('│');
                    }

                    System.out.println();
                    if (row < rowNumber) {
                        // middle row
                        System.out.print('├');
                        for (var col = 1; col < colNumber; col++) {
                            System.out.print("───" + '┼');
                        }
                        System.out.println("───" + '┤');
                    } else {
                        // draw bottom row
                        System.out.print('└');
                        for (var col = 1; col < colNumber; col++) {
                            System.out.print("───" + '┴');
                        }
                        System.out.println("───" + '┘');
                    }
                }



                // 2b. Draw Message
                Integer messageLength = (message.length() > colNumber * 4 - 1) ? message.length() : colNumber * 4 - 1;
                Integer additionalSpace = (colNumber * 4 - 1 - message.length() < 0) ? 0
                        : colNumber * 4 - 1 - message.length();
                // draw first row
                System.out.print('╔');
                for (int cnt = 0; cnt < messageLength; cnt++)
                    System.out.print('═');
                System.out.println('╗');
                // draw message row
                System.out.print('║' + message);
                for (int cnt = 0; cnt < additionalSpace; cnt++)
                    System.out.print(' ');
                System.out.println('║');
                // draw bottom row
                System.out.print('╚');
                for (int cnt = 0; cnt < messageLength; cnt++)
                    System.out.print('═');
                System.out.println('╝');

                // 2c. Await Answer
                System.out.print(">");
                String input = "";
                message = "";
                if (sc.hasNextLine() == true)
                    input = sc.nextLine() + '\n';
                else {
                    message = msgnotenough;
                    gameOver = true;
                }

                // 2d. Parse Input
                // 2dI. parse to 3 inputs.
                if (gameOver != true) {
                    String[] inputs = { "", "", "", "" };
                    int inputsidx = 0;
                    int startchar = -1;
                    /** ALESSIO: I cannot understand why you did this. One one side, you want to parse the input by
                    character (to not violate the style), and then you use substring that might violated it? */
                    for (int idx = 0; idx < input.length(); idx++) {
                        if (inputsidx >= 4) {
                            break;
                        }
                        char ch = input.charAt(idx);
                        if (startchar == -1) { // We found the start of a word
                            if (ch == 'R' || ch == 'F' || (ch >= '0' && ch <= '9')) {
                                startchar = idx;
                            }
                            continue;
                        } else if (ch == ' ' || ch == '\n') { // We found the end of a word. Process it
                            // A possible violation of style, as substring are abstract methods.
                            if (startchar != -1) {
                                inputs[inputsidx] = input.substring(startchar, idx);
                                inputsidx++;
                            }
                            startchar = -1;
                            continue;
                        } else {
                            message = msgnotvalid;
                            break;
                        }
                    }


                    // 2dII. check if inputs[] are valid
                    // check if there are exactly 3 parameter, and if 3rd parameter is F and R.
                    if (inputs[3] != "" || !((inputs[2].equals("F")) || inputs[2].equals("R"))) {
                        message = msgnotvalid;
                    } else {
                        // check if 1st para and 2nd para are numbers only.
                        for (int idx = 0; idx < inputs[0].length(); idx++) {
                            char ch = inputs[0].charAt(idx);
                            if (!(ch >= '0' && ch <= '9'))
                                message = msgnotvalid;
                        }
                        for (int idx = 0; idx < inputs[1].length(); idx++) {
                            char ch = inputs[1].charAt(idx);
                            if (!(ch >= '0' && ch <= '9'))
                                message = msgnotvalid;
                        }
                    }

                    // 2e. Handle left-click
                    if (message != msgnotvalid && (inputs[2].equals("R"))) {
                        // message = "";
                        Integer idx = (Integer.parseInt(inputs[0]) - 1) * colNumber + Integer.parseInt(inputs[1]) - 1;
                        // System.out.println("R" + idx);
                        if (opened[idx] == false) {
                            if (mined[idx] == true) {
                                gameOver = true;
                            } else {
                                opened[idx] = true;
                                if (neighbourMineCount[idx] == 0) {
                                    boolean openAllCells = false;
                                    while (!openAllCells) {
                                        // break statement: all cell with open empty neighbour are opened already
                                        openAllCells = true;
                                        for (int i = 0; i < chessboard.length(); i++) {
                                            // check only cells which is not opened
                                            if (opened[i] == false) {
                                                // not left most column
                                                if (i % colNumber != 0) {
                                                    if (i - colNumber - 1 > 0 && opened[i - colNumber - 1] == true
                                                            && neighbourMineCount[i - colNumber - 1] == 0)
                                                        openAllCells = false;
                                                    if (opened[i - 1] == true && neighbourMineCount[i - 1] == 0)
                                                        openAllCells = false;
                                                    if (i + colNumber - 1 < (rowNumber * colNumber)
                                                            && opened[i + colNumber - 1] == true
                                                            && neighbourMineCount[i + colNumber - 1] == 0)
                                                        openAllCells = false;
                                                }

                                                if (i - colNumber > 0 && opened[i - colNumber] == true
                                                        && neighbourMineCount[i - colNumber] == 0)
                                                    openAllCells = false;
                                                if (i + colNumber < (rowNumber * colNumber)
                                                        && opened[i + colNumber] == true
                                                        && neighbourMineCount[i + colNumber] == 0)
                                                    openAllCells = false;

                                                // not right most column
                                                if ((i + 1) % colNumber != 0) {
                                                    if (i - colNumber + 1 > 0 && opened[i - colNumber + 1] == true
                                                            && neighbourMineCount[i - colNumber + 1] == 0)
                                                        openAllCells = false;
                                                    if (opened[i + 1] == true && neighbourMineCount[i + 1] == 0)
                                                        openAllCells = false;
                                                    if (i + colNumber + 1 < (rowNumber * colNumber)
                                                            && opened[i + colNumber + 1] == true
                                                            && neighbourMineCount[i + colNumber + 1] == 0)
                                                        openAllCells = false;
                                                }
                                            }
                                        }
                                        // generic statement: get the chessboard
                                        if (openAllCells == false) {
                                            for (int i = 0; i < chessboard.length(); i++) {
                                                // check for all opened + 0 neighbourMineCount cell
                                                if (opened[i] == true && neighbourMineCount[i] == 0) {
                                                    // open their all neighbours
                                                    if (i % colNumber != 0) {
                                                        // top left
                                                        if (i - colNumber - 1 > 0)
                                                            opened[i - colNumber - 1] = true;
                                                        // mid left
                                                        opened[i - 1] = true;
                                                        // bot left
                                                        if (i + colNumber - 1 < (rowNumber * colNumber))
                                                            opened[i + colNumber - 1] = true;
                                                    }
                                                    // top mid
                                                    if (i - colNumber > 0)
                                                        opened[i - colNumber] = true;
                                                    // bot mid
                                                    if (i + colNumber < (rowNumber * colNumber))
                                                        opened[i + colNumber] = true;

                                                    if ((i + 1) % colNumber != 0) {
                                                        // top right
                                                        if (i - colNumber + 1 > 0)
                                                            opened[i - colNumber + 1] = true;
                                                        // mid right
                                                        opened[i + 1] = true;
                                                        // bottom right
                                                        if (i + colNumber + 1 < (rowNumber * colNumber))
                                                            opened[i + colNumber + 1] = true;
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                                // check open cell number
                                Integer openCellNumber = 0;
                                for (int i = 0; i < chessboard.length(); i++) {
                                    if (opened[i] == true)
                                        openCellNumber++;
                                }
                                if (mineNumber + openCellNumber == rowNumber * colNumber) {
                                    gameOver = true;
                                }
                            }
                        }

                    }
                    // 2f. Handle right-click
                    if (message != msgnotvalid && (inputs[2].equals("F"))) {
                        // message = "";
                        /** ALESSIO: This is another (minor) violation of the style: parseInt */
                        Integer idx = (Integer.parseInt(inputs[0]) - 1) * colNumber + Integer.parseInt(inputs[1]) - 1;
                        // System.out.println("F" + idx);
                        if (opened[idx] == false) {
                            if (flagged[idx] == true) {
                                flagged[idx] = false;
                            } else {
                                flagged[idx] = true;
                            }
                        }
                    }
                }
                // 2g. check win/lose/not enough input state.
                if (gameOver == true) {
                    Integer openCellNumber = 0;
                    for (int i = 0; i < chessboard.length(); i++) {
                        if (opened[i] == true)
                            openCellNumber++;
                    }
                    // System.out.println("message " + message);
                    if (mineNumber + openCellNumber == rowNumber * colNumber) {
                        message = msgwon;
                    } else if (message.equals(msgnotenough)) {
                        message = msgnotenough;
                    } else {
                        message = msglost;
                    }
                    // open all cells with mines
                    if (message.equals(msglost)) {
                        for (int i = 0; i < chessboard.length(); i++) {
                            if (mined[i] == true)
                                opened[i] = true;
                        }
                    }
                    // Draw message board and chess board for last time.
                    // 2gI. Draw Board
                    // print top row
                    System.out.print('┌');
                    for (var col = 1; col < colNumber; col++) {
                        System.out.print("───┬");
                    }
                    System.out.println("───┐");
                    // draw datarow + middle row
                    for (var row = 1; row <= rowNumber; row++) {
                        // data row
                        System.out.print('│');
                        for (var col = 1; col <= colNumber; col++) {
                            var index = (row - 1) * colNumber + (col - 1);
                            System.out.print(" ");
                            // 2aI. print cell logic
                            if (flagged[index] == true)
                                System.out.print("¶");
                            else {
                                if (opened[index] == true && mined[index] == true)
                                    System.out.print("*");
                                else if (opened[index] == true && neighbourMineCount[index] == 0)
                                    System.out.print("▓");
                                else if (opened[index] == true && neighbourMineCount[index] > 0)
                                    System.out.print(String.valueOf(neighbourMineCount[index]));
                                else if (opened[index] == false)
                                    System.out.print(" ");
                            }
                            System.out.print(" ");
                            System.out.print('│');
                        }
                        System.out.println();
                        if (row < rowNumber) {
                            // middle row
                            System.out.print('├');
                            for (var col = 1; col < colNumber; col++) {
                                System.out.print("───" + '┼');
                            }
                            System.out.println("───" + '┤');
                        } else {
                            // draw bottom row
                            System.out.print('└');
                            for (var col = 1; col < colNumber; col++) {
                                System.out.print("───" + '┴');
                            }
                            System.out.println("───" + '┘');
                        }
                    }
                    // 2gII. Draw Message
                    messageLength = (message.length() > colNumber * 4 - 1) ? message.length() : colNumber * 4 - 1;
                    additionalSpace = (colNumber * 4 - 1 - message.length() < 0) ? 0
                            : colNumber * 4 - 1 - message.length();
                    // draw first row
                    System.out.print('╔');
                    for (int cnt = 0; cnt < messageLength; cnt++)
                        System.out.print('═');
                    System.out.println('╗');
                    // draw message row
                    System.out.print('║' + message);
                    for (int cnt = 0; cnt < additionalSpace; cnt++)
                        System.out.print(' ');
                    System.out.println('║');
                    // draw bottom row
                    System.out.print('╚');
                    for (int cnt = 0; cnt < messageLength; cnt++)
                        System.out.print('═');
                    System.out.println('╝');

                    // close input channel
                    sc.close();
                    break;
                }
            }
        }
        // System.exit(0);
    }

}