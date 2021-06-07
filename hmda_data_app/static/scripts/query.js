const sqlQueryDiv = document.querySelector("#sqlQueryDiv");
const sqlQueryDivRow0 = document.querySelector("#sqlQueryDivRow0");
const sqlStatementTypeSelect = document.querySelector("#sqlStatementTypeSelectDivCol");
sqlStatementTypeSelect.addEventListener("change", updateSelect);
const sqlQueryDivRow1 = document.querySelector("#sqlQueryDivRow1");
const sqlQueryDivRow2 = document.querySelector("#sqlQueryDivRow2");

var rowNumber = 3;

function updateSelect(event) {
	//resets to original html above by removing added children nodes
	let nodesToRemove = []
	sqlQueryDivRow0.childNodes.forEach((node) => {
		console.log(node)
		if (node.id !== "sqlStatementTypeSelectDivCol") {
			nodesToRemove.push(node)
		}
	});
	nodesToRemove.forEach(node => node.remove())


	while (sqlQueryDivRow1.firstChild) {
		sqlQueryDivRow1.removeChild(sqlQueryDivRow1.firstChild)
	}
	while (sqlQueryDivRow2.firstChild) {
		sqlQueryDivRow2.removeChild(sqlQueryDivRow2.firstChild)
	}

	nodesToRemove = []
	sqlQueryDiv.childNodes.forEach((node) => {
		if ((node.id !== "sqlQueryDivRow0") && (node.id !== "sqlQueryDivRow1") && (node.id !== "sqlQueryDivRow2")) {
			nodesToRemove.push(node)
		}
	})
	nodesToRemove.forEach(node => node.remove())

	rowNumber = 2;

	switch (event.target.value) {
		case "SELECT":
			// // tableColumnsSelectDivCol
			sqlQueryDivRow0.appendChild(makeTableColumnsSelectDivCol(true, true));

			//fromLabel
			sqlQueryDivRow1.appendChild(makeLabel("tableColumnsSelect", "fromLabel", "FROM"))

			// //tableToSelectFromDivCol
			const tableToSelectFromDivCol = document.createElement("div");
			tableToSelectFromDivCol.className = "col-auto";
			tableToSelectFromDivCol.id = "tableToSelectFromDivCol"
			const tableToSelectFromSelect = document.createElement("select")
			tableToSelectFromSelect.className = "form-select"
			tableToSelectFromSelect.name = "tableToSelectFrom"
			tableToSelectFromSelect.appendChild(makeTableOption())
			tableToSelectFromDivCol.appendChild(tableToSelectFromSelect)
			sqlQueryDivRow1.appendChild(tableToSelectFromDivCol)


			//whereLabel
			sqlQueryDivRow2.appendChild(makeLabel("addWhereConditionButton", "whereLabel", "WHERE"))
			//addWhereConditionButton
			sqlQueryDivRow2.appendChild(makeAddWhereConditionButton())

			break;

		case "UPDATE":
			//tableToUpdateDivCol
			const tableToUpdateDivCol = document.createElement("div");
			tableToUpdateDivCol.className = "col-auto";
			tableToUpdateDivCol.id = "tableToUpdateDivCol"
			const tableToUpdateSelect = document.createElement("select");
			tableToUpdateSelect.className = "form-select"
			tableToUpdateSelect.name = "tableToUpdate"
			tableToUpdateSelect.appendChild(makeTableOption())
			tableToUpdateDivCol.appendChild(tableToUpdateSelect);
			sqlQueryDivRow0.appendChild(tableToUpdateDivCol);

			//setLabel
			sqlQueryDivRow1.appendChild(makeLabel("tableColumnsSelect", "setLabel", "SET"))

			// // tableColumnsSelectDivCol
			sqlQueryDivRow1.appendChild(makeTableColumnsSelectDivCol(true, true));

			//equalLabel
			sqlQueryDivRow1.appendChild(makeLabel("setEquationTextInput", "equalLabel", "="))

			//setEquationTextInputDivCol
			const setEquationTextInputDivCol = document.createElement("div");
			setEquationTextInputDivCol.className = "col-auto";
			setEquationTextInputDivCol.id = "setEquationTextInputDivCol";
			const setEquationTextInput = document.createElement("input");
			setEquationTextInput.type = "text";
			setEquationTextInput.name = "updateEquation"
			setEquationTextInputDivCol.appendChild(setEquationTextInput);
			sqlQueryDivRow1.appendChild(setEquationTextInputDivCol);

			//whereSelectsDivCol
			//sqlQueryDiv.appendChild(makeWhereSelects())

			break;

		case "DELETE FROM":
			break;
		default:
	}
}

function makeTableColumnsSelectDivCol(shouldAddAsterisk, shouldBeMultiple, shouldAddRowNumber = false) {
	const tableColumnsSelectDivCol = document.createElement("div");
	tableColumnsSelectDivCol.className = "col-auto";
	tableColumnsSelectDivCol.id = "tableColumnsSelectDivCol"

	tableColumnsSelectDivCol.appendChild(makeTableColumnsSelect(shouldAddAsterisk, shouldBeMultiple, shouldAddRowNumber));
	return tableColumnsSelectDivCol;
}

function makeTableColumnsSelect(shouldAddAsterisk, shouldBeMultiple, shouldAddRowNumber = false) {
	const tableColumnsSelect = document.createElement("select");
	tableColumnsSelect.className = "form-select";
	if (shouldAddRowNumber) {
		tableColumnsSelect.name = "tableColumns" + rowNumber
	} else {
		tableColumnsSelect.name = "tableColumns"
	}
	tableColumnsSelect.multiple = shouldBeMultiple;
	tableColumnsSelect.id = "tableColumnsSelect";

	//add * option to tableColumnsSelect
	if (shouldAddAsterisk) {
		const asteriskOption = document.createElement("option");
		asteriskOption.value = "asterisk";
		asteriskOption.id = "asterisk";
		asteriskOption.appendChild(document.createTextNode("asterisk"));
		tableColumnsSelect.appendChild(asteriskOption);
	}

	//add options from tableColumns to tableColumnsSelect
	const tableColumns = {{!table_info.column_names
}};//python variable
for (const tableColumn of tableColumns) {
	const option = document.createElement("option");
	option.value = tableColumn;
	option.id = tableColumn;
	option.appendChild(document.createTextNode(tableColumn));
	tableColumnsSelect.appendChild(option);
}
return tableColumnsSelect
	}

function makeTableOption() {
	const tableOption = document.createElement("option")
	tableOption.appendChild(document.createTextNode("{{!table_info.table_name}}"))//python variable
	tableOption.value = "{{!table_info.table_name}}"

	return tableOption;
}

function makeLabel(htmlFor, id, text) {
	const label = document.createElement("label");
	label.htmlFor = htmlFor;
	label.className = "col-auto";
	label.id = id;
	label.appendChild(document.createTextNode(text));

	return label;
}

function makeAddWhereConditionButton() {
	const sqlQueryDiv = document.querySelector("#sqlQueryDiv");

	addWhereConditionButton = document.createElement("button")
	addWhereConditionButton.type = "button"
	addWhereConditionButton.className = "btn btn-primary col-auto"
	addWhereConditionButton.id = "addWhereConditionButton"
	addWhereConditionButton.appendChild(document.createTextNode("Add Condition"))
	addWhereConditionButton.addEventListener("click", () => {

		const whereConditionDivRow = document.createElement("div")
		whereConditionDivRow.className = "row gy-2 gx-3 align-items-center"
		rowNumber += 1;
		whereConditionDivRow.id = "sqlQueryDivRow" + rowNumber;


		//tabelColumnsSelectDivCol
		const tableColumnsSelectDivCol = makeTableColumnsSelectDivCol(false, false, true)
		whereConditionDivRow.appendChild(tableColumnsSelectDivCol)
		// relationalOperatorSelectDivCol
		const relationalOperatorSelectDivCol = document.createElement("div")
		relationalOperatorSelectDivCol.className = "col-auto"
		whereConditionDivRow.appendChild(relationalOperatorSelectDivCol)

		const relationalOperatorSelect = document.createElement("select")
		relationalOperatorSelect.className = "form-select"
		relationalOperatorSelect.name = "relationalOperator" + rowNumber
		relationalOperatorSelectDivCol.appendChild(relationalOperatorSelect)

		relationalOperatorArray = ["=", "!=", "<", "<=", ">", ">="]
		relationalOperatorArray.forEach(relationalOperator => {
			const relationalOperatorOption = document.createElement("option")
			relationalOperatorOption.value = relationalOperator
			relationalOperatorOption.appendChild(document.createTextNode(relationalOperator))
			relationalOperatorSelect.appendChild(relationalOperatorOption)
		})


		//rightOperandTextInput
		const rightOperandTextInput = document.createElement("input")
		rightOperandTextInput.type = "text"
		rightOperandTextInput.className = "col-auto"
		rightOperandTextInput.name = "rightOperand" + rowNumber
		whereConditionDivRow.appendChild(rightOperandTextInput)
		// logicalOperatorSelectDivCol
		const logicalOperatorSelectDivCol = document.createElement("div")
		logicalOperatorSelectDivCol.className = "col-auto"
		whereConditionDivRow.appendChild(logicalOperatorSelectDivCol)

		const logicalOperatorSelect = document.createElement("select")
		logicalOperatorSelect.className = "form-select"
		logicalOperatorSelect.name = "logicalOperator" + rowNumber
		logicalOperatorSelectDivCol.appendChild(logicalOperatorSelect)

		logicalOperatorArray = ["AND", "OR"]
		logicalOperatorArray.forEach(logicalOperator => {
			const logicalOperatorOption = document.createElement("option")
			logicalOperatorOption.value = logicalOperator
			logicalOperatorOption.appendChild(document.createTextNode(logicalOperator))
			logicalOperatorSelect.appendChild(logicalOperatorOption)
		})

		sqlQueryDiv.appendChild(whereConditionDivRow)
	})

	return addWhereConditionButton
}

function resetHTML() {

}