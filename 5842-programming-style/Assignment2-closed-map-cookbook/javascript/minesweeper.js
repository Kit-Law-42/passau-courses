const readline = require('readline');
const fs = require('fs');
const FILE_ENDINGS= ".cfg";
const MSG_NOT_VALID = "The provided input is not valid!";
const MSG_WON = "You Won!";
const MSG_LOST = "You Lost!";
const MSG_NOT_ENOUGH = "Not enough inputs!";
const VALID_INPUT = ['F', 'R'];
const MAX_COLUMN_SIZE = 20;
const MAX_ROW_SIZE = 20;

//constant of token of table drawings
const T_TOP_LEFT = '┌'; //┌
const T_TOP_MID = '┬'; //┬
const T_TOP_RIGHT = '┐'; //┐
const T_MID_LEFT = '├'; //├
const T_MID_MID = '┼'; //┼
const T_MID_RIGHT = '┤'; //┤
const T_BOT_LEFT = '└'; //└
const T_BOT_MID = '┴'; //┴
const T_BOT_RIGHT = '┘'; //┘
const T_HORIZONTAL = '─'; //─
const T_VERTICAL = '│'; //│

//constant of token of message table
const M_TOP_LEFT = '╔'; //╔
const M_TOP_RIGHT = '╗'; //╗
const M_VERTICAL = '║'; //║
const M_BOT_LEFT = '╚'; //╚
const M_HORIZONTAL = '═'; //═
const M_BOT_RIGHT = '╝'; //╝

const TOKEN_MINE = '*';
const TOKEN_FLAG = '¶';
const TOKEN_EMPTY = '▓';

var fileName = "";
var lines = "";
var opened = [];
var flagged = [];
var mined =[];
var neighborMineCount= [];

var rowNumber =0;
var colNumber =0;
var message = "";
var userInputString ="";
var userInputs = new Array(3);
var gameOver = false;
var mineNumber = 0;
var openCellNumber = 0;

var RL = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

var checkArgsLength = function(args){
    if (args.length  < 3){
        process.exit(1);
    }
    else{
        fileName = args[2];
    }
}

var readValidateCfgFile = function()
{
    // 1. check file existence and extension, file name have higher priority than file existence.
    
    var extension = fileName.toLowerCase().slice(fileName.length - FILE_ENDINGS.length);
    var file = fileName.slice(0, fileName.length - FILE_ENDINGS.length)

    // 1a. check extension
    if (extension != FILE_ENDINGS || file.length ==0)
    {
        process.exit(2);
    }    

    // 1b. check existence.
    try{
	    fs.accessSync(fileName, fs.F_OK);    
    }
    catch (err){
        process.exit(1);
    }

    // 2. check board validity.
    try
    {
        const data = fs.readFileSync(fileName, 'utf-8'); 	  
		// 2a. check line endings for the last row
        if (data.endsWith('\n') == true){
            lines = data.toString().split("\n");     
            lines.pop(); //remove last element
        }
        else{
            process.exit(2);
        }
    
        // 2b. check column size and row size.
        var columnsize = lines.length;
        var rowSize = 0;
        
        if (columnsize < 1 || columnsize > MAX_COLUMN_SIZE)
        {
            process.exit(2);
        }
        else{
            process.exitCode = 0;
            for(i in lines) 
            {
                regex = /^([\*\.])+$/g;
                var row = lines[i];
                if (i==0) {rowSize = row.length;}
                if (row.length != rowSize || (!(row.match(regex)) || rowSize < 1 || rowSize > MAX_ROW_SIZE))
                {
                    // not end with [\n] and row length != column size, return 2
                    process.exit(2);
                }
            }
        }

        // 2c. check corner case 1 : 1*1 mineBoard is not valid
        if ((columnsize == 1 && rowSize ==1))
        {
            process.exit(2);
        }
    }
    catch (err){
        // 2d. any error when reading mal-formed file, return 1.
        process.exit(1);
    }
}

var createBasicBoard = function(){

    // 1. Define Cell class
    opened = Array.from(Array(lines.length), () => new Array(lines[0].length))
    flagged = Array.from(Array(lines.length), () => new Array(lines[0].length))
    mined = Array.from(Array(lines.length), () => new Array(lines[0].length))
    neighborMineCount = Array.from(Array(lines.length), () => new Array(lines[0].length))

    // 2. loop lines
    for(rowNumber = 1; rowNumber <= lines.length; rowNumber++ )
	{
		for(colNumber = 1; colNumber <= lines[rowNumber-1].length; colNumber++ )
		{
            if (lines[rowNumber-1][colNumber-1] == ".")
            {              
                opened[rowNumber-1][colNumber-1] = false;
                flagged[rowNumber-1][colNumber-1] = false;
                mined[rowNumber-1][colNumber-1] = false;
                neighborMineCount[rowNumber-1][colNumber-1] = 0;
            }
            else
            {              
                opened[rowNumber-1][colNumber-1] = false;
                flagged[rowNumber-1][colNumber-1] = false;
                mined[rowNumber-1][colNumber-1] = true;
                neighborMineCount[rowNumber-1][colNumber-1] = 0;
                mineNumber++;
            }
		}
    }
    rowNumber--;
    colNumber--;

    // 3. check if mine numbers is equal to board size
    if (mineNumber >= rowNumber*colNumber)
    {
        process.exit(2);
    }
}

var updateNeighborMineCounts = function()
{
	for( var row = 1; row <= rowNumber; row++ )
	{
		for( var column = 1; column <= colNumber; column++ )
		{
			if( !mined[row-1][column-1])
			{
                // 1. get neighbour list
                var neighbors = [];
                neighbors.push( (row - 1) + "_" + (column - 1) );
                neighbors.push( (row - 1) + "_" + column );
                neighbors.push( (row - 1) + "_" + (column + 1) );
                neighbors.push( row + "_" + (column - 1) );
                neighbors.push( row + "_" + (column + 1) );
                neighbors.push( (row + 1) + "_" + (column - 1) );
                neighbors.push( (row + 1) + "_" + column );
                neighbors.push( (row + 1) + "_" + (column + 1) );
                
                // 2. calculate mine count
				var neighborMineTotal = 0;
				for( var i = 0; i < neighbors.length; i++ )
				{
                    var [tempRow, tempCol] = neighbors[i].split("_");
                    var mineCount = 0;
                    if ( tempRow >0 && tempRow <= rowNumber && tempCol >0 && tempCol <= colNumber)
                    {
                        mineCount = mined[tempRow-1][tempCol-1] ? 1 : 0;
                    }
					neighborMineTotal += mineCount;
				}
                neighborMineCount[row-1][column-1] = neighborMineTotal;
                
			}
		}
	}
}

//--------------------------------------------------------------//

var prepareFinalDraw = function()
{
    if (message == MSG_LOST)
    {
        for( var row = 1; row <= rowNumber; row++ )
        {
            for( var column = 1; column <= colNumber; column++ )
            {
                if (mined[row-1][column-1]) {
                    opened[row-1][column-1] = true;
                }
            }
        }
    }
}

var drawBoard = function(){


    // draw first row
    process.stdout.write(T_TOP_LEFT);
    for (var col =1; col < colNumber; col++)
    {          
        process.stdout.write(T_HORIZONTAL.repeat(3) + T_TOP_MID);
    }
    process.stdout.write(T_HORIZONTAL.repeat(3) + T_TOP_RIGHT  + '\n');
    // draw datarow + middle row
    for (var row =1; row <= rowNumber; row++)
    {
        // data row
        process.stdout.write(T_VERTICAL);
        for( var col = 1; col <= colNumber; col++ )
		{
            process.stdout.write(" ");
            if (flagged[row-1][col-1]){ process.stdout.write(TOKEN_FLAG);}
            // in displaying final mine map, this line have to come first to avoid bug.
            else if (opened[row-1][col-1] && mined[row-1][col-1]) {process.stdout.write( TOKEN_MINE);}
            else if (opened[row-1][col-1] && neighborMineCount[row-1][col-1] ==0) {process.stdout.write( TOKEN_EMPTY);}
            else if (opened[row-1][col-1] && neighborMineCount[row-1][col-1] >0) {process.stdout.write( neighborMineCount[row-1][col-1].toString());}
            else process.stdout.write(" ");
            process.stdout.write(" " + T_VERTICAL );
        }
        process.stdout.write('\n');
        if (row< rowNumber)
        {
            // middle row
            process.stdout.write(T_MID_LEFT);
            for (var col =1; col < colNumber; col++)
            {
                process.stdout.write(T_HORIZONTAL.repeat(3) + T_MID_MID);
            }
            process.stdout.write(T_HORIZONTAL.repeat(3) + T_MID_RIGHT+ '\n');
        }
        else
        {
            // draw bottom row
            process.stdout.write(T_BOT_LEFT);
            for (var col =1; col < colNumber; col++)
            {
                process.stdout.write(T_HORIZONTAL.repeat(3) + T_BOT_MID);
            }
            process.stdout.write(T_HORIZONTAL.repeat(3) + T_BOT_RIGHT  + '\n');
        }
    }

}

var drawMessage = function()
{
    //determine size of column, compare colNumber and Message length
    var messageLength = (message.length > colNumber*4-1) ? message.length : colNumber *4-1;
    var additionalSpace = (colNumber*4-1-message.length <0 )? 0: colNumber*4-1-message.length;
    // draw first row
    process.stdout.write(M_TOP_LEFT + M_HORIZONTAL.repeat(messageLength) + M_TOP_RIGHT+ '\n');
    // draw message row
    process.stdout.write(M_VERTICAL + message + " ".repeat(additionalSpace)+ M_VERTICAL + '\n');
    // draw bottom row
    process.stdout.write(M_BOT_LEFT + M_HORIZONTAL.repeat(messageLength) + M_BOT_RIGHT+ '\n');
}

var parseInput = function()
{
    var inputs = userInputString.split(/(\s+)/).filter( e => e.trim().length > 0)
    if (inputs.length !=3) 
    {
        message = MSG_NOT_VALID;
    }
    else
    {
        userInputs = inputs;
        // check validity of user's input
        if (userInputs[0] < 1 || userInputs[1] < 1 || userInputs[0]> rowNumber || userInputs[1] > colNumber|| 
            (VALID_INPUT.indexOf(userInputs[2]) < 0) || (userInputs[0].indexOf('.') >= 0) || (userInputs[1].indexOf('.')>= 0))
        {
            message = MSG_NOT_VALID;
        }
        else{          
            message = ""; //reset the message.
        }
        
    }
} 

var handleLeftClick = function()
{
    if (userInputs[2] == "R"&& message == "")
    {
        var input0 = userInputs[0] -1;
        var input1 = userInputs[1] -1;
        if( !opened[input0][input1])
        {
            flagged[input0][input1] = false;
            if( mined[input0][input1])
            {
                message = MSG_LOST;
                gameOver = true;
            }
            else
            {
                opened[input0][input1] = true;
                openCellNumber++;
                if( neighborMineCount[input0][input1] == 0)
                {
                    var openAllCells = false;    
                    while (!openAllCells) 
                    {
                        openAllCells = true;
                        var cellSet = new Set();
                        //add all neighbours cell of empty cell to cellSet, and open them all
                        for (var row =1; row <= rowNumber; row++ )
                        {                     
                            for( var col = 1; col <= colNumber; col++ )
                            {                             
                                if (opened[row-1][col-1] == true && neighborMineCount[row-1][col-1] == 0)
                                {
                                    cellSet.add( (row - 1) + "_" + (col - 1) );
                                    cellSet.add( (row - 1) + "_" + col );
                                    cellSet.add( (row - 1) + "_" + (col + 1) );
                                    cellSet.add( row + "_" + (col - 1) );
                                    cellSet.add( row + "_" + (col + 1) );
                                    cellSet.add( (row + 1) + "_" + (col - 1) );
                                    cellSet.add( (row + 1) + "_" + col );
                                    cellSet.add( (row + 1) + "_" + (col + 1) );
                                }                              
                            }
                        }
                        // open all cells
                        for (var id of cellSet)
                        {
                            var [tempRow, tempCol] = id.split("_");
                            if( tempRow >0 && tempRow <= rowNumber && tempCol >0 && tempCol <= colNumber
                                 && opened[tempRow-1][tempCol-1] == false)
                            {
                                opened[tempRow-1][tempCol-1] = true;
                                openCellNumber++;
                            }
                        }
                        cellSet.clear();

                        // check if there is any open cell with 0 neighbour count.
                        for (var row =1; row <= rowNumber; row++)
                        {                     
                            for( var col = 1; col <= colNumber; col++ )
                            {
                                if (opened[row-1][col-1] == false ){
                                    var neighbourCellSet = new Set();
                                    neighbourCellSet.add( (row - 1) + "_" + (col - 1) );
                                    neighbourCellSet.add( (row - 1) + "_" + col );
                                    neighbourCellSet.add( (row - 1) + "_" + (col + 1) );
                                    neighbourCellSet.add( row + "_" + (col - 1) );
                                    neighbourCellSet.add( row + "_" + (col + 1) );
                                    neighbourCellSet.add( (row + 1) + "_" + (col - 1) );
                                    neighbourCellSet.add( (row + 1) + "_" + col );
                                    neighbourCellSet.add( (row + 1) + "_" + (col + 1) );
                                    for (var neighbourId of neighbourCellSet)
                                    {
                                        var [tempRow, tempCol] = neighbourId.split("_");
                                        if ( tempRow >0 && tempRow <= rowNumber && tempCol >0 && tempCol <= colNumber)
                                        {
                                            if(neighborMineCount[tempRow-1][tempCol-1] ==0 && opened[tempRow-1][tempCol-1] == true)
                                            {
                                                openAllCells = false;
                                            }
                                        }
                                    }                           
                                }
                            }
                        }   
                    }
                }
            }
        }
        else
        {
            message = MSG_NOT_VALID;
        }
        // Reset userInputs
        userInputs = new Array(3);
        // check if winning state is reach.
        if (mineNumber + openCellNumber == rowNumber * colNumber)
        {
            message = MSG_WON;
            gameOver = true;
        }
    }
}

var handleRightClick = function()
{
    if (userInputs[2] == "F" && message == "")
    {      
        var input0 = userInputs[0] -1;
        var input1 = userInputs[1] -1;
        if(!opened[input0][input1])
        {
            if(!flagged[input0][input1]) // if cell is not flagged
            {
                flagged[input0][input1] = true;      
            }
            else if(flagged[input0][input1]) // if cell is flagged
            {
                flagged[input0][input1] = false;
            }
        }
        // Reset userInputs
        userInputs = new Array(3);
    }
}

var inputPanel = function () {
     // a possible violation in cookbook style.
    // this logic is not placed in main()
    // could not find better way to put this logic yet.

    // draw Board
    drawBoard();
    drawMessage();

    // awaiting additional input from user.
    RL.question('>', function (answer) {      
        userInputString = answer;
        parseInput();
        handleLeftClick();
        handleRightClick();
        //base case, for reading interface recursion
        if (message == MSG_WON || message == MSG_NOT_ENOUGH || message == MSG_LOST)
        {
            prepareFinalDraw();
            drawBoard();
            drawMessage();
            //closing reading interface and returning 0.
            RL.close();
            process.exit(0); 
        }
        inputPanel(); //Calling this function again to ask new question
    })
}

var closeReadlineInterface = function(){
    // a possible violation in cookbook style.
    // this logic is not placed in main()
    // could not find better way to put this logic yet.
    RL.on('close', function(answer) {
        // EOF
        if (gameOver != true){
            message = MSG_NOT_ENOUGH;
            prepareFinalDraw();
            drawBoard();
            drawMessage();
        }
        process.exit(0);
       });
}

/*
Rules:
1. No long jumps
2. Complexity of control flow tamed by dividing the large problem into smaller units using procedural abstraction
3. Procedures may share state in the form of global variables
4. The large problem is solved by applying the procedures, one after the other, that change, or add to, the shared state
*/
var main = function(args) {
    // TODO Implement me !
    checkArgsLength(args);
    readValidateCfgFile();
    createBasicBoard();
    updateNeighborMineCounts();
    // A violation in cookbook Style for below 2 function. There are loop and subfunction inside them, 
    // which is required by the read interface
    // although all variables are still manipulated by global variables.
    inputPanel();
    closeReadlineInterface();
}

if (require.main === module) {
    // Pass the arguments to the function
    // argv[0] -> node
    // argv[1] -> this script
    // argv[2] -> the first real input
    // Pass the arguments to the function
    main(process.argv);
}

/*
  Export the main function so it can be called from the tests. This let us testing the
  app without creating a subprocess but YOU need to take care of cleaning up and
  initializing the app.
*/
module.exports.main = main