const readline = require('readline');
const fs = require('fs');
const rowEndings = "";
const fileEndings= ".cfg";

//constant of token of table drawings
const ttopleft = '\u250C'; //┌
const ttopmid = '\u252C'; //┬
const ttopright = '\u2510'; //┐
const tmidleft = '\u251C'; //├
const tmidmid = '\u253C'; //┼
const tmidright = '\u2524'; //┤
const tbotleft = '\u2514'; //└
const tbotmid = '\u2534'; //┴
const tbotright = '\u2518'; //┘
const thorizontal = '\u2500'; //─
const tvertical = '\u2502'; //│

//constant of token of message table
const mtopleft = '\u2554'; //╔
const mtopmid = '\u2550'; //═
const mtopright = '\u2557'; //╗
const mmidleft = '\u2551'; //║
const mmidright = '\u2551'; //║
const mbotleft = '\u255A'; //╚
const mbotmid = '\u2550'; //═
const mbotright = '\u255D'; //╝

const mine = '*';
const flag = '¶';
const empty = '▓';

const msgnotvalid = "The provided input is not valid!";
const msgwon = "You Won!";
const msglost = "You Lost!";
const msgnotenough = "Not enough inputs!";
const validinput = ['F', 'R'];
const maxColumnSize = 20;
var rowNumber =0;
var colNumber =0;
var message = "";
var input ="";
var gameOver = false;
var mineNumber = 0;
var openCellNumber = 0;


/** ALESSIO: Naming of functions that are not constructores shoud be in lowercase. */
function Cell( row, column, opened, flagged, mined, neighborMineCount ) 
{
	return {
		id: row + "_" + column,
		row: row,
		column: column,	
		opened: opened,
		flagged: flagged,
		mined: mined,
		neighborMineCount: neighborMineCount
	}
}

var checkBoard = function(fileName)
{
    // 1. check file existence and extension
    // file name have higher priority than file existence.
    var extension = fileName.toLowerCase().slice(fileName.length - fileEndings.length);
    var file = fileName.slice(0, fileName.length - fileEndings.length)
    if (extension != fileEndings || file.length ==0)
    {
        process.exitCode = 2;
        return 
    }    
    try{
	    fs.accessSync(fileName, fs.F_OK);    
    }
    catch (err){
        process.exitCode = 1;
        return
    }
    // 2. check board validity.
    try
    {
        const data = fs.readFileSync(fileName, 'utf-8'); 	  
		// Converting Raw Buffer to text 
        // data using tostring function. 
        var lines;
        if (data.endsWith('\n') == true){
            lines = data.toString().split("\n");     
            lines.pop(); //remove last element
        }
        else{
            process.exitCode =2;
            return
        }
        //console.log("lines.length:", lines.length);
        var columnsize = lines.length;
        var rowSize = 0;
        // A. empty file, return 2
        if (columnsize < 1 || columnsize > maxColumnSize)
        {
            //console.log("ohhh");
            process.exitCode = 2; 
            return
        }
        else{
            process.exitCode = 0;
            //console.log("ohhhhh");
            for(i in lines) 
            {
                regex = /^([\*\.])+$/g;
                var endings = lines[i].slice(lines[i].length - rowEndings.length);
                var row = lines[i].slice(0, lines[i].length - rowEndings.length);
                if (i==0) {rowSize = row.length;}
                if (/*endings != rowEndings ||*/ row.length != rowSize || (!(row.match(regex))))
                {
                    // not end with [\n] and row length != column size, return 2
                    process.exitCode = 2;
                    return
                }
            }
        }
        if ((columnsize == 1 && rowSize ==1) ||  rowSize > maxColumnSize)
        {
            process.exitCode = 2;
            return
        }
        //All checking asserted(except no. of mines), create board.
        board = Board(lines);
        return board;
    }
    catch (err){
        process.exitCode = 1;
        return
    }
}

function Board(lines)
{
	var board = {};
    //Read lines and count rowNumber and countNumber
	for(rowNumber = 1; rowNumber <= lines.length; rowNumber++ )
	{
		for(colNumber = 1; colNumber <= lines[rowNumber-1].length - rowEndings.length; colNumber++ )
		{
            if (lines[rowNumber-1][colNumber-1] == ".")
            {
                board[rowNumber + "_" + colNumber] = Cell( rowNumber, colNumber, false, false, false, 0 );
            }
            else
            {
                board[rowNumber + "_" + colNumber] = Cell( rowNumber, colNumber, false, false, true, 0 );
                mineNumber++;
            }
		}
    }
    rowNumber--;
    colNumber--;
    if (mineNumber >= rowNumber*colNumber)
    {
        process.exitCode = 2;
        return
    }
    
	board = calculateNeighborMineCounts( board, rowNumber, colNumber);
	return board;
}


var handleLeftClick = function(row, column)
{
    var cell = board[(row) + "_" + (column)];
    if( !cell.opened )
    {
        cell.flagged = false;
        if( cell.mined )
        {
            gameOver = true;
        }
        else
        {
            cell.opened = true;
            openCellNumber++;
            if( cell.neighborMineCount == 0 )
            {

                var neighbors = getNeighbors((row) + "_" + (column));
                for( var i = 0; i < neighbors.length; i++ )
                {
                    var neighbor = neighbors[i];
                    if(  typeof board[neighbor] !== 'undefined' &&
                            !board[neighbor].flagged && !board[neighbor].opened )
                    {
                        handleLeftClick((neighbor.split('_')[0]), (neighbor.split('_')[1]));
                    }
                }

            }
        }
    }
    else
    {
        message = msgnotvalid;
    }
}

var handleRightClick = function(row, column)
{
    var cell = board[(row) + "_" + (column)];
    if( !cell.opened )
    {
        if( !cell.flagged ) // if cell is not flagged
        {
            cell.flagged = true;      
        }
        else if( cell.flagged ) // if cell is flagged
        {
            cell.flagged = false;
        }
    }
    else // show er msg if flag an open cell
    {
        //message = msgnotvalid;
    }
}

var calculateNeighborMineCounts = function( board, rowNumber, colNumber )
{
	var cell;
	var neighborMineCount = 0;
	for( var row = 1; row <= rowNumber; row++ )
	{
		for( var column = 1; column <= colNumber; column++ )
		{
			var id = row + "_" + column;
			cell = board[id];
			if( !cell.mined )
			{
				var neighbors = getNeighbors(id);
				neighborMineCount = 0;
				for( var i = 0; i < neighbors.length; i++ )
				{
					neighborMineCount += isMined( board, neighbors[i] );
				}
				cell.neighborMineCount = neighborMineCount;
			}
		}
	}
	return board;
}


var getNeighbors = function(id)
{
	var row = parseInt(id.split('_')[0]);
	var column = parseInt(id.split('_')[1]);
	var neighbors = [];
	neighbors.push( (row - 1) + "_" + (column - 1) );
	neighbors.push( (row - 1) + "_" + column );
	neighbors.push( (row - 1) + "_" + (column + 1) );
	neighbors.push( row + "_" + (column - 1) );
	neighbors.push( row + "_" + (column + 1) );
	neighbors.push( (row + 1) + "_" + (column - 1) );
	neighbors.push( (row + 1) + "_" + column );
	neighbors.push( (row + 1) + "_" + (column + 1) );

	return neighbors
}


var isMined = function( board, id )
{	
	var cell = board[id];
	var mined = 0;
	if( typeof cell !== 'undefined' )
	{
		mined = cell.mined ? 1 : 0;
	}
	return mined;
}

// ALESSIO: This does not seem to make any sense? You implemented a function of one line, that creates a global variable
// validBoard, that is also returned by the function?
var ReadCfg = function(fileName)
{
  // TO-DO read .cfg files
  // create class board by reading files

	validBoard = checkBoard(fileName);
	return validBoard;
}

var DrawCell = function(cell)
{
    if (cell.flagged){ return flag;}
    // in displaying final mine map, this line have to come first to avoid bug.
    if (cell.opened && cell.mined) return mine;
    if (cell.opened && cell.neighborMineCount ==0) return empty;
    if (cell.opened && cell.neighborMineCount >0) return cell.neighborMineCount.toString();

    return " ";
}

var DrawBoard = function(board){
    // draw first row
    process.stdout.write(ttopleft);
    for (var col =1; col < colNumber; col++)
    {          
        process.stdout.write(thorizontal.repeat(3) + ttopmid);
    }
    process.stdout.write(thorizontal.repeat(3) + ttopright + rowEndings + '\n');
    // draw datarow + middle row
    for (var row =1; row <= rowNumber; row++)
    {
        // data row
        process.stdout.write(tvertical);
        for( var col = 1; col <= colNumber; col++ )
		{
            var id = row + "_" + col;
            cell = board[id];
            process.stdout.write(" " + DrawCell(cell) + " " + tvertical );
        }
        process.stdout.write(rowEndings+ '\n');
        if (row< rowNumber)
        {
            // middle row
            process.stdout.write(tmidleft);
            for (var col =1; col < colNumber; col++)
            {
                process.stdout.write(thorizontal.repeat(3) + tmidmid);
            }
            process.stdout.write(thorizontal.repeat(3) + tmidright+ rowEndings+ '\n');
        }
        else
        {
            // draw bottom row
            process.stdout.write(tbotleft);
            for (var col =1; col < colNumber; col++)
            {
                process.stdout.write(thorizontal.repeat(3) + tbotmid);
            }
            process.stdout.write(thorizontal.repeat(3) + tbotright + rowEndings + '\n');
        }
    }

}

var DrawMessage = function(colNumber)
{
    //determine size of column, compare colNumber and Message length
    messageLength = (message.length > colNumber*4-1) ? message.length : colNumber *4-1;
    additionalSpace = (colNumber*4-1-message.length <0 )? 0: colNumber*4-1-message.length;
    // draw first row
    process.stdout.write(mtopleft + mtopmid.repeat(messageLength) + mtopright+ rowEndings+ '\n');
    // draw message row
    process.stdout.write(mmidleft + message + " ".repeat(additionalSpace)+ mmidright+ rowEndings+ '\n');
    // draw bottom row
    process.stdout.write(mbotleft + mbotmid.repeat(messageLength) + mbotright+ rowEndings+ '\n');
}


var ParseInput = function(answer)
{
    // parse input
    var inputs = answer.split(/(\s+)/).filter( e => e.trim().length > 0)
    //console.log(inputs.length)
    if (inputs.length !=3) 
    {
        message = msgnotvalid;
    }
    else
    {
        //console.log(inputs[0] , inputs[1], inputs[2])
        //console.log((validinput.indexOf(inputs[2]) < 0))
        // check all invalid input of test
        if (inputs[0] < 1 || inputs[1] < 1 || inputs[0]> rowNumber || inputs[1] > colNumber|| 
            (validinput.indexOf(inputs[2]) < 0) || (inputs[0].indexOf('.') ==0) || (inputs[1].indexOf('.')==0))
        {
            message = msgnotvalid;
        }
        else{          
            message = ""; //reset the message.
            if (inputs[2] == "R")
            {
                handleLeftClick(inputs[0], inputs[1]);
            }
            else if (inputs[2] == "F")
            {
                handleRightClick(inputs[0], inputs[1]);
            }
        }
        //check if winning state is reach.
        if (mineNumber + openCellNumber == rowNumber * colNumber)
        {
            gameOver = true;
        }
    }
} 



var DrawFinalResult = function(msg)
{
    //console.clear()
    if (mineNumber + openCellNumber == rowNumber * colNumber) //winning state
    {
        message = msgwon;
    }
    else if (msg == msgnotenough)
    {
        message = msg;
    }
    else //losing state
    {
        message = msg;
        for( var row = 1; row <= rowNumber; row++ )
        {
            for( var column = 1; column <= colNumber; column++ )
            {
                var id = row + "_" + column;
                if (isMined(board, id)) {
                    cell = board[id];
                    cell.opened = true;
                    }
            }
        }
    }
    DrawBoard(board);
    DrawMessage(colNumber);
    process.exitCode = 0;
}
// var rl = readline.createInterface({
//     input: process.stdin,
//     output: process.stdout
// });

var InputPanel = function (rl) {
    //get answers.
    // 2. draw sweeper board
    process.exitCode = 0;
    DrawBoard(board);
    DrawMessage(colNumber);

    
    // 3a. wait for input
    rl.question('>', function (answer) {      
        // 3b. parse input
        ParseInput(answer);
        if (gameOver == true) //we need some base case, for recursion
        {
            // gameOver can be win or lost.
            DrawFinalResult(msglost);
            rl.close();
            return process.exitCode; //closing RL and returning from function.
        }
        InputPanel(rl); //Calling this function again to ask new question
    })
    
};

var main = function(args) 
{
	// Implement me !
    // 1. read file
    //console.log(args.length)
    if (args.length  < 3){
        process.exitCode = 1;
        /** ALESSIO: Fair, but you could also have used process.exit(exitCode) */
        return process.exitCode
    }

    /** ALESSIO: Does this also the validation? */
    board = ReadCfg(args[2]);
    
    if (process.exitCode === 0)
    {
        var rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
        InputPanel(rl);
        rl.on('close', function(answer) {
            // EOF
            if (gameOver != true){
                message = msgnotenough;
                DrawFinalResult(msgnotenough);
            }
            return process.exitCode;
           });
        //draw board for the last time.
        gameOver = false;
    }
    //return
    //console.log("exitcode: ", process.exitCode)
    return process.exitCode
}

if (require.main === module) {
	// Pass the arguments to the function
    // argv[0] -> node
    // argv[1] -> this script
    // argv[2] -> the first real input
    main(process.argv);
}

/*
  Export the main function so it can be called from the tests. This let us testing the
  app without creating a subprocess but YOU need to take care of cleaning up and
  initializing the app.
*/
module.exports.main = main