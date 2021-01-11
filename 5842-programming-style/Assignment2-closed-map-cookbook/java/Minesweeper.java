import java.io.File;
import java.io.FileNotFoundException;
import java.util.HashMap;
import java.util.HashSet;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Scanner;
import java.util.Set;
import java.util.function.Supplier;
import java.util.function.BiConsumer;
import java.util.function.BiFunction;
import java.util.function.BiPredicate;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Predicate;

public class Minesweeper {

    private static void validate_file_name(String FILE_ENDINGS, String[] argumentArray) {

        if (argumentArray.length > 0) {
            String fileFullName = argumentArray[0];
            String extension = fileFullName.toLowerCase().substring(fileFullName.length() - FILE_ENDINGS.length());
            String fileName = fileFullName.substring(0, fileFullName.length() - FILE_ENDINGS.length());

            if (fileName.length() == 0 || !extension.equals(FILE_ENDINGS)) {
                System.exit(2);
            }
        } else {
            System.exit(1);
        }

    }

    @SuppressWarnings("unchecked")
    private static void validate_parse_file_content(Map<String, Object> self, int maxColumnSize, int maxRowSize,
            String fileFullName) {

        Integer rowNumber = 0;
        Integer colNumber = 0;
        File f = new File(fileFullName);
        if (!f.exists()) {
            System.exit(1);
        } else if (f.isDirectory()) {
            System.exit(2);
        }

        String chessboardString = "";
        Scanner myReader;
        try {
            myReader = new Scanner(f);

            int tempColSize = 0;
            while (myReader.hasNextLine()) {
                String data = myReader.nextLine();

                for (int i = 0; i < data.length(); i++) {
                    if (!(data.charAt(i) == '*' || data.charAt(i) == '.')) {
                        System.exit(2);
                    }
                }
                chessboardString += data;
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
            if (rowNumber == 1 && colNumber == 1) {
                System.exit(2);
            }
            if (rowNumber > maxRowSize || rowNumber < 1 || chessboardString.length() == 0) {
                System.exit(2);
            }
            myReader.close();
        } catch (FileNotFoundException e) {
            System.exit(2);
        }

        char[][] chessBoard2Darray = new char[rowNumber][colNumber];
        for (int row = 0; row < rowNumber; row++) {
            chessBoard2Darray[row] = chessboardString.substring(row * colNumber, (row + 1) * colNumber).toCharArray();
        }

        ((Consumer<Integer>) self.get("setRowNumber")).accept(rowNumber);
        ((Consumer<Integer>) self.get("setColNumber")).accept(colNumber);
        ((Consumer<char[][]>) self.get("setChessBoard")).accept(chessBoard2Darray);
        // return (char[][]) ((Supplier<char[][]>) self.get("getChessBoard")).get();
    }

    @SuppressWarnings("unchecked")
    private static void update_chessboard_mineCount(Map<String, Object> self, int maxColumnSize, int maxRowSize) {

        int rowNumber = (int) ((Supplier<Integer>) self.get("getRowNumber")).get();
        int colNumber = (int) ((Supplier<Integer>) self.get("getColNumber")).get();
        char[][] chessboard = (char[][]) ((Supplier<char[][]>) self.get("getChessBoard")).get();
        Boolean[][] flagged = new Boolean[rowNumber][colNumber];
        Boolean[][] mined = new Boolean[rowNumber][colNumber];
        Boolean[][] opened = new Boolean[rowNumber][colNumber];
        Integer[][] neighbourMineCount = new Integer[rowNumber][colNumber];
        int mineNumber = 0;

        // **************************************//
        for (int row = 0; row < rowNumber; row++) {
            for (int col = 0; col < colNumber; col++) {
                flagged[row][col] = false;
                opened[row][col] = false;
                mined[row][col] = (chessboard[row][col] == '*') ? true : false;
                if (chessboard[row][col] == '*')
                    mineNumber++;
            }
        }
        // check number of mine.
        if (mineNumber == rowNumber * colNumber)
            System.exit(2);

        // calculate neightbourMineCount
        for (var row = 1; row <= rowNumber; row++) {
            for (var column = 1; column <= colNumber; column++) {
                if (!mined[row - 1][column - 1]) {
                    // 1. get neighbour list
                    ArrayList<String> neighbors = new ArrayList<String>();
                    neighbors.add("" + (row - 1) + "_" + (column - 1));
                    neighbors.add((row - 1) + "_" + column);
                    neighbors.add((row - 1) + "_" + (column + 1));
                    neighbors.add(row + "_" + (column - 1));
                    neighbors.add(row + "_" + (column + 1));
                    neighbors.add((row + 1) + "_" + (column - 1));
                    neighbors.add((row + 1) + "_" + column);
                    neighbors.add((row + 1) + "_" + (column + 1));

                    // 2. calculate mine count
                    var neighborMineTotal = 0;
                    for (var i = 0; i < neighbors.size(); i++) {
                        int tempRow = Integer.parseInt(neighbors.get(i).split("_")[0]);
                        int tempCol = Integer.parseInt(neighbors.get(i).split("_")[1]);
                        var mineCount = 0;
                        if (tempRow > 0 && tempRow <= rowNumber && tempCol > 0 && tempCol <= colNumber) {
                            mineCount = mined[tempRow - 1][tempCol - 1] ? 1 : 0;
                        }
                        neighborMineTotal += mineCount;
                    }
                    neighbourMineCount[row - 1][column - 1] = neighborMineTotal;
                } else {
                    // this cell is mined
                    neighbourMineCount[row - 1][column - 1] = 0;
                }
            }
        }
        ((Consumer<Boolean[][]>) self.get("setOpened")).accept(opened);
        ((Consumer<Boolean[][]>) self.get("setFlagged")).accept(flagged);
        ((Consumer<Boolean[][]>) self.get("setMined")).accept(mined);
        ((Consumer<Integer[][]>) self.get("setNeighbourMineCount")).accept(neighbourMineCount);
    }

    @SuppressWarnings("unchecked")
    private static void print_chess_board(Map<String, Object> self) {
        int rowNumber = (int) ((Supplier<Integer>) self.get("getRowNumber")).get();
        int colNumber = (int) ((Supplier<Integer>) self.get("getColNumber")).get();
        Boolean[][] mined = (Boolean[][]) ((Supplier<Boolean[][]>) self.get("getMined")).get();
        Boolean[][] flagged = (Boolean[][]) ((Supplier<Boolean[][]>) self.get("getFlagged")).get();
        Boolean[][] opened = (Boolean[][]) ((Supplier<Boolean[][]>) self.get("getOpened")).get();
        Integer[][] neighbourMineCount = (Integer[][]) ((Supplier<Integer[][]>) self.get("getNeighbourMineCount"))
                .get();

        System.out.print('┌');
        for (var col = 1; col < colNumber; col++) {
            System.out.print("───┬");
        }
        System.out.println("───┐");

        for (var row = 0; row < rowNumber; row++) {
            // data row
            System.out.print('│');
            for (var col = 0; col < colNumber; col++) {
                System.out.print(" ");
                // 2aI. print cell logic
                if (flagged[row][col] == true)
                    System.out.print("¶");
                else {
                    if (opened[row][col] == true && mined[row][col] == true)
                        System.out.print("*");
                    else if (opened[row][col] == true && neighbourMineCount[row][col] == 0)
                        System.out.print("▓");
                    else if (opened[row][col] == true && neighbourMineCount[row][col] > 0)
                        /** ALESSIO: Probably String.valueOf is unecessary */
                        System.out.print(neighbourMineCount[row][col]);
                    else if (opened[row][col] == false)
                        System.out.print(" ");
                }
                System.out.print(" ");
                System.out.print('│');
            }
            System.out.println();
            if (row < rowNumber - 1) {
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
    }

    @SuppressWarnings("unchecked")
    private static void print_message_board(Map<String, Object> self, String message) {

        int colNumber = (int) ((Supplier<Integer>) self.get("getColNumber")).get();

        Integer messageLength = (message.length() > colNumber * 4 - 1) ? message.length() : colNumber * 4 - 1;
        Integer additionalSpace = (colNumber * 4 - 1 - message.length() < 0) ? 0 : colNumber * 4 - 1 - message.length();
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
    }

    @SuppressWarnings("unchecked")
    private static Map<String, Object> open_all_mine(Map<String, Object> self) {
        int rowNumber = (int) ((Supplier<Integer>) self.get("getRowNumber")).get();
        int colNumber = (int) ((Supplier<Integer>) self.get("getColNumber")).get();
        Boolean[][] mined = (Boolean[][]) ((Supplier<Boolean[][]>) self.get("getMined")).get();
        Boolean[][] opened = (Boolean[][]) ((Supplier<Boolean[][]>) self.get("getOpened")).get();

        for (var row = 1; row <= rowNumber; row++) {
            for (var column = 1; column <= colNumber; column++) {
                if (mined[row - 1][column - 1]) {
                    opened[row - 1][column - 1] = true;
                }
            }
        }
        ((Consumer<Boolean[][]>) self.get("setOpened")).accept(opened);
        ((Consumer<Boolean[][]>) self.get("setMined")).accept(mined);

        return self;
    }

    @SuppressWarnings("unchecked")
    private static void open_cell(Map<String, Object> self, String[] coordinates) {

        int rowNumber = (int) ((Supplier<Integer>) self.get("getRowNumber")).get();
        int colNumber = (int) ((Supplier<Integer>) self.get("getColNumber")).get();
        Boolean[][] flagged = (Boolean[][]) ((Supplier<Boolean[][]>) self.get("getFlagged")).get();
        Boolean[][] mined = (Boolean[][]) ((Supplier<Boolean[][]>) self.get("getMined")).get();
        Boolean[][] opened = (Boolean[][]) ((Supplier<Boolean[][]>) self.get("getOpened")).get();
        Integer[][] neighbourMineCount = (Integer[][]) ((Supplier<Integer[][]>) self.get("getNeighbourMineCount"))
                .get();
        int openRow = Integer.parseInt(coordinates[0]) - 1;
        int openCol = Integer.parseInt(coordinates[1]) - 1;
        // int openCellNumber = 0;
        if (!opened[openRow][openCol]) {
            flagged[openRow][openCol] = false;
            if (!mined[openRow][openCol]) {
                opened[openRow][openCol] = true;
                if (neighbourMineCount[openRow][openCol] == 0) {
                    Boolean openAllCells = false;
                    while (!openAllCells) {
                        openAllCells = true;
                        Set<String> cellSet = new HashSet<String>();
                        // add all neighbours cell of empty cell to cellSet, and open them all
                        for (var row = 1; row <= rowNumber; row++) {
                            for (var col = 1; col <= colNumber; col++) {
                                if (opened[row - 1][col - 1] == true && neighbourMineCount[row - 1][col - 1] == 0) {
                                    cellSet.add((row - 1) + "_" + (col - 1));
                                    cellSet.add((row - 1) + "_" + col);
                                    cellSet.add((row - 1) + "_" + (col + 1));
                                    cellSet.add(row + "_" + (col - 1));
                                    cellSet.add(row + "_" + (col + 1));
                                    cellSet.add((row + 1) + "_" + (col - 1));
                                    cellSet.add((row + 1) + "_" + col);
                                    cellSet.add((row + 1) + "_" + (col + 1));
                                }
                            }
                        }
                        // open all cells
                        for (String id : cellSet) {
                            int tempRow = Integer.parseInt(id.split("_")[0]);
                            int tempCol = Integer.parseInt(id.split("_")[1]);
                            if (tempRow > 0 && tempRow <= rowNumber && tempCol > 0 && tempCol <= colNumber
                                    && opened[tempRow - 1][tempCol - 1] == false) {
                                opened[tempRow - 1][tempCol - 1] = true;
                            }
                        }
                        cellSet.clear();

                        // check if there is any open cell with 0 neighbour count.
                        for (var row = 1; row <= rowNumber; row++) {
                            for (var col = 1; col <= colNumber; col++) {
                                if (opened[row - 1][col - 1] == false) {
                                    Set<String> neighbourCellSet = new HashSet<String>();
                                    neighbourCellSet.add((row - 1) + "_" + (col - 1));
                                    neighbourCellSet.add((row - 1) + "_" + col);
                                    neighbourCellSet.add((row - 1) + "_" + (col + 1));
                                    neighbourCellSet.add(row + "_" + (col - 1));
                                    neighbourCellSet.add(row + "_" + (col + 1));
                                    neighbourCellSet.add((row + 1) + "_" + (col - 1));
                                    neighbourCellSet.add((row + 1) + "_" + col);
                                    neighbourCellSet.add((row + 1) + "_" + (col + 1));
                                    for (String neighbourId : neighbourCellSet) {
                                        int tempRow = Integer.parseInt(neighbourId.split("_")[0]);
                                        int tempCol = Integer.parseInt(neighbourId.split("_")[1]);
                                        if (tempRow > 0 && tempRow <= rowNumber && tempCol > 0
                                                && tempCol <= colNumber) {
                                            if (neighbourMineCount[tempRow - 1][tempCol - 1] == 0
                                                    && opened[tempRow - 1][tempCol - 1] == true) {
                                                openAllCells = false;
                                            }
                                        }
                                    }
                                }
                            }
                        }

                    }
                }
            } else {
                opened[openRow][openCol] = true;
            }
        }
        ((Consumer<Boolean[][]>) self.get("setOpened")).accept(opened);
        ((Consumer<Boolean[][]>) self.get("setFlagged")).accept(flagged);
        ((Consumer<Boolean[][]>) self.get("setMined")).accept(mined);
        ((Consumer<Integer[][]>) self.get("setNeighbourMineCount")).accept(neighbourMineCount);

        // return self;
    }

    @SuppressWarnings("unchecked")
    private static void flag_cell(Map<String, Object> self, String[] coordinates) {

        Boolean[][] flagged = (Boolean[][]) ((Supplier<Boolean[][]>) self.get("getFlagged")).get();
        Boolean[][] opened = (Boolean[][]) ((Supplier<Boolean[][]>) self.get("getOpened")).get();
        int row = Integer.parseInt(coordinates[0]) - 1;
        int col = Integer.parseInt(coordinates[1]) - 1;

        if (opened[row][col] == false) {
            if (flagged[row][col] == true) {
                flagged[row][col] = false;
            } else {
                flagged[row][col] = true;
            }
        }
        ((Consumer<Boolean[][]>) self.get("setOpened")).accept(opened);
        ((Consumer<Boolean[][]>) self.get("setFlagged")).accept(flagged);
        // return self;
    }

    @SuppressWarnings("unchecked")
    private static Boolean is_lost(Map<String, Object> self) {
        int rowNumber = (int) ((Supplier<Integer>) self.get("getRowNumber")).get();
        int colNumber = (int) ((Supplier<Integer>) self.get("getColNumber")).get();
        Boolean[][] opened = (Boolean[][]) ((Supplier<Boolean[][]>) self.get("getOpened")).get();
        Boolean[][] mined = (Boolean[][]) ((Supplier<Boolean[][]>) self.get("getMined")).get();

        for (var row = 1; row <= rowNumber; row++) {
            for (var col = 1; col <= colNumber; col++) {
                if (opened[row - 1][col - 1] == true && mined[row - 1][col - 1] == true)
                    return true;
            }
        }
        return false;
    }

    @SuppressWarnings("unchecked")
    private static Boolean is_win(Map<String, Object> self) {

        int rowNumber = (int) ((Supplier<Integer>) self.get("getRowNumber")).get();
        int colNumber = (int) ((Supplier<Integer>) self.get("getColNumber")).get();
        Boolean[][] opened = (Boolean[][]) ((Supplier<Boolean[][]>) self.get("getOpened")).get();
        Boolean[][] mined = (Boolean[][]) ((Supplier<Boolean[][]>) self.get("getMined")).get();
        int mineNumber = 0;
        int openCellNumber = 0;
        for (var row = 1; row <= rowNumber; row++) {
            for (var col = 1; col <= colNumber; col++) {
                if (opened[row - 1][col - 1] == true && mined[row - 1][col - 1] == false)
                    openCellNumber++;
                if (mined[row - 1][col - 1] == true)
                    mineNumber++;
            }
        }

        if (mineNumber + openCellNumber == rowNumber * colNumber) {
            return true;
        } else {
            return false;
        }
    }

    private static Boolean is_user_input_valid(String userInput) {
        userInput = userInput.trim();
        if (userInput.split(" ").length < 3)
            return false;

        String[] userInputs = userInput.split(" ");
        for (int idx = 0; idx < userInputs[0].length(); idx++) {
            char ch = userInputs[0].charAt(idx);
            if (!(ch >= '0' && ch <= '9'))
                return false;
        }
        for (int idx = 0; idx < userInputs[1].length(); idx++) {
            char ch = userInputs[1].charAt(idx);
            if (!(ch >= '0' && ch <= '9'))
                return false;
        }
        if (!((userInputs[2].equals("F")) || userInputs[2].equals("R"))) {
            return false;
        }
        return true;
    }

    @SuppressWarnings("unchecked")
    private static Boolean is_valid_coordinates(Map<String, Object> self, String[] coordinates) {
        int rowNumber = (int) ((Supplier<Integer>) self.get("getRowNumber")).get();
        int colNumber = (int) ((Supplier<Integer>) self.get("getColNumber")).get();

        if (Integer.parseInt(coordinates[0]) < 1 || Integer.parseInt(coordinates[0]) > rowNumber
                || Integer.parseInt(coordinates[1]) < 1 || Integer.parseInt(coordinates[1]) > colNumber) {
            return false;
        }
        return true;
    }

    @SuppressWarnings("unchecked")
    public static void main(String[] args) {
        // - The larger problem is decomposed into 'things' that make sense for the
        // problem domain
        //
        // - Each 'thing' is a map from keys to values. Some values are
        // procedures/functions, other are data.
        // - No static variables, as it violate encapsulation between things.

        // --------------------------------------------------------------------------------//
        // Configuration Manager
        // They are constants, so I put them directly into function, rather than
        // declaring variables.
        Map<String, Supplier<?>> configuration_Manager = new HashMap<String, Supplier<?>>();
        configuration_Manager.put("FILE_ENDINGS", () -> ".cfg");
        configuration_Manager.put("MSG_NOT_VALID", () -> "The provided input is not valid!");
        configuration_Manager.put("MSG_WON", () -> "You Won!");
        configuration_Manager.put("MSG_LOST", () -> "You Lost!");
        configuration_Manager.put("MSG_NOT_ENOUGH", () -> "Not enough inputs!");
        configuration_Manager.put("MAX_COLUMN_SIZE", () -> 20);
        configuration_Manager.put("MAX_ROW_SIZE", () -> 20);
        // --------------------------------------------------------------------------------//
        // File Parse Manager
        // Manage file parsing and put them into variables.
        // Enforce encapsulation by declaring get set methods.
        Map<String, Object> chess_board_Manager = new HashMap<String, Object>();

        chess_board_Manager.put("_chessBoard", "");
        chess_board_Manager.put("_flagged", "");
        chess_board_Manager.put("_mined", "");
        chess_board_Manager.put("_opened", "");
        chess_board_Manager.put("_neighbourMineCount", "");

        chess_board_Manager.put("_rowNumber", 0);
        chess_board_Manager.put("_colNumber", 0);
        chess_board_Manager.put("_mineNumber", 0);
        chess_board_Manager.put("_message", "");

        chess_board_Manager.put("getChessBoard",
                (Supplier<char[][]>) () -> (char[][]) chess_board_Manager.get("_chessBoard"));
        chess_board_Manager.put("getFlagged",
                (Supplier<Boolean[][]>) () -> (Boolean[][]) chess_board_Manager.get("_flagged"));
        chess_board_Manager.put("getMined",
                (Supplier<Boolean[][]>) () -> (Boolean[][]) chess_board_Manager.get("_mined"));
        chess_board_Manager.put("getOpened",
                (Supplier<Boolean[][]>) () -> (Boolean[][]) chess_board_Manager.get("_opened"));
        chess_board_Manager.put("getNeighbourMineCount",
                (Supplier<Integer[][]>) () -> (Integer[][]) chess_board_Manager.get("_neighbourMineCount"));

        chess_board_Manager.put("getRowNumber", (Supplier<Integer>) () -> (int) chess_board_Manager.get("_rowNumber"));
        chess_board_Manager.put("getColNumber", (Supplier<Integer>) () -> (int) chess_board_Manager.get("_colNumber"));
        chess_board_Manager.put("getMineNumber",
                (Supplier<Integer>) () -> (int) chess_board_Manager.get("_mineNumber"));
        chess_board_Manager.put("getMessage", (Supplier<String>) () -> (String) chess_board_Manager.get("_message"));

        chess_board_Manager.put("setChessBoard", (Consumer<char[][]>) (x) -> chess_board_Manager.put("_chessBoard", x));
        chess_board_Manager.put("setFlagged", (Consumer<Boolean[][]>) (x) -> chess_board_Manager.put("_flagged", x));
        chess_board_Manager.put("setMined", (Consumer<Boolean[][]>) (x) -> chess_board_Manager.put("_mined", x));
        chess_board_Manager.put("setOpened", (Consumer<Boolean[][]>) (x) -> chess_board_Manager.put("_opened", x));
        chess_board_Manager.put("setNeighbourMineCount",
                (Consumer<Integer[][]>) (x) -> chess_board_Manager.put("_neighbourMineCount", x));

        chess_board_Manager.put("setRowNumber", (Consumer<Integer>) (x) -> chess_board_Manager.put("_rowNumber", x));
        chess_board_Manager.put("setColNumber", (Consumer<Integer>) (x) -> chess_board_Manager.put("_colNumber", x));
        chess_board_Manager.put("setMineNumber", (Consumer<Integer>) (x) -> chess_board_Manager.put("_mineNumber", x));
        chess_board_Manager.put("setMessage", (Consumer<String>) (x) -> chess_board_Manager.put("_message", x));

        // get only 2 constants from configuration manager, do not pass all hashmap.
        chess_board_Manager.put("parse_cfg_file",
                (Consumer<String>) (String fileName) -> validate_parse_file_content(chess_board_Manager,
                        (int) configuration_Manager.get("MAX_COLUMN_SIZE").get(),
                        (int) configuration_Manager.get("MAX_ROW_SIZE").get(), fileName));
        chess_board_Manager.put("update_chessboard_with_mineCount",
                (Consumer<Map<String, Object>>) (Map<String, Object> manager) -> update_chessboard_mineCount(manager,
                        (int) configuration_Manager.get("MAX_COLUMN_SIZE").get(),
                        (int) configuration_Manager.get("MAX_ROW_SIZE").get()));
        chess_board_Manager.put("print_chess_board",
                (Consumer<Map<String, Object>>) (Map<String, Object> boardManager) -> print_chess_board(boardManager));
        chess_board_Manager.put("print_message_board",
                (BiConsumer<Map<String, Object>, String>) (Map<String, Object> boardManager,
                        String Message) -> print_message_board(boardManager, Message));
        chess_board_Manager.put("open_all_mine",
                (Consumer<Map<String, Object>>) (Map<String, Object> boardManager) -> open_all_mine(boardManager));
        chess_board_Manager.put("open_cell",
                (BiConsumer<Map<String, Object>, String[]>) (Map<String, Object> boardManager,
                        String[] Coordinates) -> open_cell(boardManager, Coordinates));
        chess_board_Manager.put("flag_cell",
                (BiConsumer<Map<String, Object>, String[]>) (Map<String, Object> boardManager,
                        String[] Coordinates) -> flag_cell(boardManager, Coordinates));
        chess_board_Manager.put("is_valid_coordinates",
                (BiPredicate<Map<String, Object>, String[]>) (Map<String, Object> boardManager,
                        String[] Coordinates) -> is_valid_coordinates(boardManager, Coordinates));
        chess_board_Manager.put("is_win",
                (Predicate<Map<String, Object>>) (Map<String, Object> boardManager) -> is_win(boardManager));
        chess_board_Manager.put("is_lost",
                (Predicate<Map<String, Object>>) (Map<String, Object> boardManager) -> is_lost(boardManager));
        // ------------------------------------------------------------------------------------------------//
        // Parse User Input Manager
        Map<String, Object> user_Input_Parse_Manager = new HashMap<String, Object>();

        user_Input_Parse_Manager.put("validate_file_name", (BiConsumer<String, String[]>) (String fileEndings,
                String[] fileName) -> validate_file_name(fileEndings, fileName));
        user_Input_Parse_Manager.put("is_user_input_valid",
                (Predicate<String>) (String userInput) -> is_user_input_valid(userInput));

        // there are only 3 inputs, let them separately are more clear than an extra
        // input n.
        user_Input_Parse_Manager.put("get_user_1st_input",
                (Function<String, String>) (String userInput) -> userInput.trim().split(" ")[0]);
        user_Input_Parse_Manager.put("get_user_2nd_input",
                (Function<String, String>) (String userInput) -> userInput.trim().split(" ")[1]);
        user_Input_Parse_Manager.put("get_user_3rd_input",
                (Function<String, String>) (String userInput) -> userInput.trim().split(" ")[2]);

        // Example usage:
        // 1st get, get result in HashMap which return lambda function () -> ".cfg"
        // 2nd get , get result from Supplier
        // System.out.println(configuration_object.get("FILE_ENDINGS").get());
        // -------------------------------------------------------------------------//
        // Program starts.
        String message = "";
        // 1. Validate if fileName is valid
        ((BiConsumer<String, String[]>) user_Input_Parse_Manager.get("validate_file_name"))
                .accept((String) configuration_Manager.get("FILE_ENDINGS").get(), args);

        // 2. Validate file content is valid
        ((Consumer<String>) chess_board_Manager.get("parse_cfg_file")).accept(args[0]);

        // 3. update mineCount
        ((Consumer<Map<String, Object>>) chess_board_Manager.get("update_chessboard_with_mineCount"))
                .accept(chess_board_Manager);

        Scanner sc = new Scanner(System.in);
        while (true) {

            // print chess Board
            ((Consumer<Map<String, Object>>) chess_board_Manager.get("print_chess_board")).accept(chess_board_Manager);
            // print message board
            ((BiConsumer<Map<String, Object>, String>) chess_board_Manager.get("print_message_board"))
                    .accept(chess_board_Manager, message);
            System.out.print(">");
            String input = "";

            if (sc.hasNextLine() == true)
                input = sc.nextLine() + '\n';
            else {
                message = (String) configuration_Manager.get("MSG_NOT_ENOUGH").get();
            }

            if (!(message.equals((String) configuration_Manager.get("MSG_NOT_ENOUGH").get())
                    || message.equals((String) configuration_Manager.get("MSG_WON").get())
                    || message.equals((String) configuration_Manager.get("MSG_LOST").get()))) {
                // validate input
                if (((Predicate<String>) user_Input_Parse_Manager.get("is_user_input_valid")).test(input)) {

                    String[] coordinates = {
                            ((Function<String, String>) user_Input_Parse_Manager.get("get_user_1st_input"))
                                    .apply(input),
                            ((Function<String, String>) user_Input_Parse_Manager.get("get_user_2nd_input"))
                                    .apply(input) };

                    if (((BiPredicate<Map<String, Object>, String[]>) chess_board_Manager.get("is_valid_coordinates"))
                            .test(chess_board_Manager, coordinates)) {
                        // handle left click
                        if (((Function<String, String>) user_Input_Parse_Manager.get("get_user_3rd_input")).apply(input)
                                .equals("R")) {

                            ((BiConsumer<Map<String, Object>, String[]>) chess_board_Manager.get("open_cell"))
                                    .accept(chess_board_Manager, coordinates);
                        }
                        // handle right-click
                        else {
                            ((BiConsumer<Map<String, Object>, String[]>) chess_board_Manager.get("flag_cell"))
                                    .accept(chess_board_Manager, coordinates);
                        }
                        // check winning condition
                        if (((Predicate<Map<String, Object>>) chess_board_Manager.get("is_win"))
                                .test(chess_board_Manager)) {
                            message = (String) configuration_Manager.get("MSG_WON").get();

                            ((Consumer<Map<String, Object>>) chess_board_Manager.get("print_chess_board"))
                                    .accept(chess_board_Manager);
                            ((BiConsumer<Map<String, Object>, String>) chess_board_Manager.get("print_message_board"))
                                    .accept(chess_board_Manager, message);
                            sc.close();
                            break;
                        }
                        // check losing condition
                        else if (((Predicate<Map<String, Object>>) chess_board_Manager.get("is_lost"))
                                .test(chess_board_Manager)) {
                            message = (String) configuration_Manager.get("MSG_LOST").get();
                            ((Consumer<Map<String, Object>>) chess_board_Manager.get("open_all_mine"))
                                    .accept(chess_board_Manager);
                            ((Consumer<Map<String, Object>>) chess_board_Manager.get("print_chess_board"))
                                    .accept(chess_board_Manager);
                            ((BiConsumer<Map<String, Object>, String>) chess_board_Manager.get("print_message_board"))
                                    .accept(chess_board_Manager, message);
                            sc.close();
                            break;

                        } else {
                            message = "";
                        }
                    } else {
                        message = (String) configuration_Manager.get("MSG_NOT_VALID").get();
                    }
                } else {
                    message = (String) configuration_Manager.get("MSG_NOT_VALID").get();
                }
            } else {
                ((Consumer<Map<String, Object>>) chess_board_Manager.get("print_chess_board"))
                        .accept(chess_board_Manager);
                ((BiConsumer<Map<String, Object>, String>) chess_board_Manager.get("print_message_board"))
                        .accept(chess_board_Manager, message);
                System.exit(0);
            }
        }

    }

}