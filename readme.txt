README

Los programas solicitados en los ejercicios se encuentran en el
directorio:

    exercisesTesting/programs/


--------------------------------------------------
SISTEMAS OPERATIVOS
Ejercicios V1 (1–6)
--------------------------------------------------

Nota:
En los ejemplos de salida del terminal, las indentaciones pueden diferir
ligeramente de la salida real del simulador. Esta diferencia es
únicamente estética.


==================================================
Ejercicio 1
Implementación de la instrucción MEMADD
==================================================

En primer lugar se añade una nueva entrada en el fichero
instructions.def:

    INST(CALL)
    INST(MEMADD)

A continuación se añade un nuevo caso en el switch de la función
Processor_DecodeAndExecuteInstruction().

Fragmento relevante del código:

    case MEMADD_INST:
        registerMAR_CPU = operand1;
        Buses_write_AddressBus_From_To(CPU, MMU);

        registerCTRL_CPU = CTRLREAD;
        Buses_write_ControlBus_From_To(CPU, MMU);

        switch (operand2) {

            case REGISTERACCUMULATOR_CPU:
                tempAcc = registerAccumulator_CPU;
                registerAccumulator_CPU += registerMBR_CPU.cell;
                break;

            case REGISTERA_CPU:
                tempAcc = registerA_CPU;
                registerAccumulator_CPU =
                    registerA_CPU + registerMBR_CPU.cell;
                break;

            case REGISTERB_CPU:
                tempAcc = registerB_CPU;
                registerAccumulator_CPU =
                    registerB_CPU + registerMBR_CPU.cell;
                break;

            default:
                tempAcc = registerAccumulator_CPU;
                registerAccumulator_CPU += registerMBR_CPU.cell;
        }

        Processor_CheckOverflow(
            operand1,
            registerMBR_CPU.cell,
            registerAccumulator_CPU
        );

        registerPC_CPU++;

Esta instrucción suma el contenido de la celda de memoria indicada por
operand1 con el valor del registro indicado por operand2.

El resultado de la suma se almacena siempre en el registro acumulador,
tal como especifica el enunciado del ejercicio.

Si el identificador de registro no corresponde con ninguno de los
registros válidos (acumulador, A o B), se utiliza el acumulador como
registro por defecto.


==================================================
Ejercicio 2
Función ComputerSystem_PrintProgramList
==================================================

Se implementa la función ComputerSystem_PrintProgramList() para mostrar
en pantalla los programas de usuario contenidos en el vector
programList.

Debido al momento en el que se llama a esta función, es posible iterar
únicamente sobre el número real de programas recibidos como parámetros
del simulador.

Código de la función:

    void ComputerSystem_PrintProgramList(int argc) {

        ComputerSystem_DebugMessage(TIMED_MESSAGE, 101, INIT);

        for (int i = 1; i <= argc && programList[i] != NULL; i++) {

            ComputerSystem_DebugMessage(
                NO_TIMED_MESSAGE,
                102,
                INIT,
                programList[i]->executableName,
                programList[i]->arrivalTime
            );
        }
    }

El bucle comienza en la posición 1 del vector programList porque la
posición 0 está reservada para el proceso SystemIdleProcess, que no es
un programa de usuario.


==================================================
Ejercicio 3
Comparación con la Arrival Time Queue
==================================================

Se añade la llamada a la función anterior dentro de
ComputerSystem_PowerOn():

    int programsFromFilesBaseIndex =
        ComputerSystem_ObtainProgramList(argc, argv, paramIndex);

    ComputerSystem_PrintProgramList(argc);

Al ejecutar el simulador se obtiene una salida similar a la siguiente:

    [0] STARTING simulation
    [0] User programs list:

        Program [prog] with arrival time [0]

    [0] Arrival Time Queue:

        [SystemIdleProcess, 0, DAEMON-PROGRAM]
        [prog, 0, USER-PROGRAM]

La lista de programas mostrada por la función y el contenido de la
arrival time queue difieren porque la función implementada únicamente
muestra programas de usuario.

En concreto, el bucle comienza en la posición 1 del vector programList,
por lo que el proceso SystemIdleProcess (que se encuentra en la
posición 0) no se muestra en la lista.


==================================================
Ejercicio 4
Ejecución simultánea de dos programas
==================================================

Si se ejecuta el simulador con el mismo programa dos veces:

    ./Simulator --debugSections=HD programVerySimple programVerySimple

se observa que el programa no llega a ejecutarse dos veces.

Esto ocurre porque muchos de los programas de ejemplo finalizan con la
instrucción HALT. Cuando se ejecuta HALT, la simulación completa termina
inmediatamente, por lo que el segundo proceso no llega a ejecutarse.

Para solucionar este problema, se sustituye la instrucción HALT por
TRAP 3.

La llamada al sistema TRAP 3 permite finalizar el proceso actual de
forma controlada y devolver el control al sistema operativo, que puede
planificar la ejecución de otros procesos.

Un posible programa prog-V1-E4 es el siguiente:

    30
    5
    ADD 0 -3
    WRITE 15
    TRAP 3

Al ejecutar el simulador con dos instancias de este programa, ambos
procesos se ejecutan correctamente.


==================================================
Ejercicio 5
Ejecución de un programa inexistente
==================================================

Si se ejecuta el simulador indicando un programa que no existe en el
sistema de ficheros, el simulador muestra un mensaje de error.

Inicialmente el programa aparece en la lista de programas introducidos
por el usuario, ya que el simulador construye esta lista directamente a
partir de los parámetros de la línea de comandos.

Sin embargo, cuando el planificador a largo plazo
(OperatingSystem_LongTermScheduler) intenta crear el proceso asociado,
se comprueba si el fichero realmente existe.

Si el fichero no existe, se muestra un mensaje de error indicando que
el programa no es válido y el proceso no llega a ejecutarse.


==================================================
Ejercicio 6
Número de procesos superior a la tabla de procesos
==================================================

La tabla de procesos tiene una capacidad limitada. En la versión
proporcionada del simulador, el tamaño máximo es de cuatro procesos
(incluyendo el proceso SystemIdleProcess).

Si se ejecuta el simulador con más programas de los que caben en la
tabla de procesos, se produce un acceso fuera de los límites del array
processTable.

Esto provoca un error de tipo "segmentation fault".

Para solucionar este problema se realizan dos modificaciones.

Primera modificación:

En la función OperatingSystem_CreateProcess() se comprueba si existe
una entrada libre en la tabla de procesos. Si no existe, la función
termina inmediatamente devolviendo el código de error NOFREEENTRY.

    assignedPID = OperatingSystem_ObtainAnEntryInTheProcessTable();

    if (assignedPID == NOFREEENTRY)
        return NOFREEENTRY;

Segunda modificación:

En la función OperatingSystem_LongTermScheduler() se añade un nuevo
caso para detectar esta situación de error y mostrar el mensaje
correspondiente.

De esta forma, cuando el número de procesos supera la capacidad de la
tabla, el simulador informa del error pero continúa ejecutando
correctamente aquellos procesos que sí caben en la tabla.

==================================================
Ejercicio 7
==================================================

Ejecución con prioridad negativa:

[0] 
Process [0] created from program [SystemIdleProcess]
[0] 
Process [1] created from program [invalidProgram]
[1] 
{0D 000 000}
 IRET 0 0 (PID: 1, PC: 0, Accumulator: 0, PSW: 0002 [--------------Z-], IntLine: [0000])
[2] 
{01 00A 002}
 ADD 10 2 (PID: 1, PC: 1, Accumulator: 12, PSW: 0000 [----------------], IntLine: [0000])
[3] 
{08 014 000}
 WRITE 20 0 (PID: 1, PC: 2, Accumulator: 12, PSW: 0000 [----------------], IntLine: [0000])
[4] 
{04 003 000}
 TRAP 3 0 (PID: 1, PC: 3, Accumulator: 12, PSW: 0000 [----------------], IntLine: [0004])
[5] 
{0C 002 000}
 OS 2 0 (PID: 1, PC: 242, Accumulator: 12, PSW: 0080 [--------X-------], IntLine: [0000])
[6] 
Process [1 - invalidProgram] has requested to terminate
[6] 
The SystemIdleProcess is ready to shut down the simulator when dispatched...
[7] 
{0D 000 000}
 IRET 0 0 (PID: 0, PC: 3, Accumulator: 12, PSW: 0080 [--------X-------], IntLine: [0000])
[8] 
{04 003 000}
 TRAP 3 0 (PID: 0, PC: 4, Accumulator: 12, PSW: 0080 [--------X-------], IntLine: [0004])
[9] 
{0C 002 000}
 OS 2 0 (PID: 0, PC: 242, Accumulator: 12, PSW: 0080 [--------X-------], IntLine: [0000])
[10] 
Process [0 - SystemIdleProcess] has requested to terminate
[10] 
The system will shut down now...
[11] 
{0D 000 000}
 IRET 0 0 (PID: -1, PC: 241, Accumulator: 12, PSW: 0080 [--------X-------], IntLine: [0000])
[12] 
{0B 000 000}
 HALT 0 0 (PID: -1, PC: 241, Accumulator: 12, PSW: 0081 [--------X------S], IntLine: [0000])
[12] 
END of the simulation


Ejecución con tamaño negativo:

41 messages loaded from file 'messagesTCH.txt'
2 messages loaded from file 'messagesSTD.txt'
0 Asserts Loaded
[0] STARTING simulation
[0] User programs list: Program [invalidProgram] with arrival time [0]
[0] Arrival Time Queue: [SystemIdleProcess, 0, DAEMON-PROGRAM], [invalidProgram, 0, USER-PROGRAM]
[0] Process [0] created from program [SystemIdleProcess]
[0] Process [1] created from program [invalidProgram]
[1] {0D 000 000} IRET 0 0 (PID: 1, PC: 0, Accumulator: 0, PSW: 0002 [--------------Z-], IntLine: [0000])
[2] _ _ _
[3] _ _ _
[4] _ _ _
[5] _ _ _
[6] _ _ _
[7] _ _ _
[8] _ _ _
[9] _ _ _
[10] _ _ _
[11] _ _ _
[12] _ _ _
...
Comienza a tener un comportamiento extraño

-----------------------------
A) Modificar "OperatingSystem_CreateProcess"
-----------------------------
Esta es la parte modificada de la función

// This function creates a process from an executable program
int OperatingSystem_CreateProcess(int indexOfExecutableProgram) {
    // Más código antes...

	// Obtain the memory requirements of the program
	processSize=OperatingSystem_ObtainProgramSize(programFile);
	if(processSize == PROGRAMNOTVALID) return PROGRAMNOTVALID;

	// Obtain the priority for the process
	priority=OperatingSystem_ObtainPriority(programFile);
	if(priority == PROGRAMNOTVALID) return PROGRAMNOTVALID;

    //.. Resto del código...
}

-----------------------------
B) Modificar "OperatingSystem_LongTermScheduler"
-----------------------------

Modificamos la función añadiendo un case PROGRAMNOTVALID al switch

int OperatingSystem_LongTermScheduler() {  
	int createdProcessPID, i,
		numberOfSuccessfullyCreatedProcesses=0;
	while (OperatingSystem_IsThereANewProgram()!=EMPTYQUEUE) {
		i=Heap_poll(arrivalTimeQueue,QUEUE_ARRIVAL,&numberOfProgramsInArrivalTimeQueue);
		createdProcessPID=OperatingSystem_CreateProcess(i);
		switch (createdProcessPID) {
			case PROGRAMNOTVALID: // New case (modification)
				ComputerSystem_DebugMessage(TIMED_MESSAGE, 51, ERROR, programList[i]->executableName, "invalid priority or size");
				break;
    // Más código...
}


==================================================
Ejercicio 8
==================================================
El programa entra en un bucle infinito si se ejecuta con el tamaño 65, pero termina su ejecución adecuadamente cuando se modifica a 55. El SO originalmente comprueba que el tamaño sea demasiado grande y devuelve un código de error, pero este no se comprueba. Por tanto, el programa se carga igualmente en memoria de manera indebida, dando lugar a comportamiento no deseado. Con el valor 55, no se produce este código de error, luego funciona adecuadamente.

-----------------------------
A) Modificar "OperatingSystem_CreateProcess"
-----------------------------

Parte modificada de la función:
int OperatingSystem_CreateProcess(int indexOfExecutableProgram) {
	//... Código previo

	// Obtain enough memory space
 	loadingPhysicalAddress=OperatingSystem_ObtainMainMemory(processSize, assignedPID);
	if(loadingPhysicalAddress == TOOBIGPROCESS) return TOOBIGPROCESS;
    //.. Resto de la función
}

Ahora sí se comprueba el código de error en caso de haberlo y se abandona adecuadamente. Por simplicidad, solo se incluye la parte modificada de la función, el código al completo está en el archivo Operatingsystem.c.

-----------------------------
B) Modificar "OperatingSystem_LongTermScheduler"
-----------------------------
Parte modificada: Añadimos un case de TOOBIGPROCESS

int OperatingSystem_LongTermScheduler() {  
	int createdProcessPID, i,
		numberOfSuccessfullyCreatedProcesses=0;
	while (OperatingSystem_IsThereANewProgram()!=EMPTYQUEUE) {
		i=Heap_poll(arrivalTimeQueue,QUEUE_ARRIVAL,&numberOfProgramsInArrivalTimeQueue);
		createdProcessPID=OperatingSystem_CreateProcess(i);
		switch (createdProcessPID) {
            //...Mas casos...
			case TOOBIGPROCESS:
				ComputerSystem_DebugMessage(TIMED_MESSAGE, 52, ERROR, programList[i]->executableName);
				break;
		    //...mas casos...
		}
	}
	// Return the number of succesfully created processes
	return numberOfSuccessfullyCreatedProcesses;
}

==================================================
Ejercicio 9
==================================================
Al ejecutarlo, pasa esto: exercisesTesting/programs/prog-V1-E9

41 messages loaded from file 'messagesTCH.txt'
2 messages loaded from file 'messagesSTD.txt'
0 Asserts Loaded
[0]
STARTING simulation
[0]
User programs list:
 Program [prog-V1-E9] with arrival time [0]
[0]
Arrival Time Queue:
  [SystemIdleProcess, 0, DAEMON-PROGRAM]
  [prog-V1-E9, 0, USER-PROGRAM]

[0]
Process [0] created from program [SystemIdleProcess]

[0]
Process [1] created from program [prog-V1-E9]

[1]
{0D 000 000}
IRET 0 0 (PID: 1, PC: 0, Accumulator: 0, PSW: 0002 [--------------Z-], IntLine: [0000])

[2]
{01 013 000}
ADD 19 0 (PID: 1, PC: 1, Accumulator: 19, PSW: 0000 [----------------], IntLine: [0000])

[3]
{08 014 000}
WRITE 20 0 (PID: 1, PC: 2, Accumulator: 19, PSW: 0000 [----------------], IntLine: [0000])


Al igual que antes, se produce un código de error que no se gestiona:

-----------------------------
A) Modificar "OperatingSystem_CreateProcess"
-----------------------------
Parte modificada:
int OperatingSystem_CreateProcess(int indexOfExecutableProgram) {
    //...Código previo
	// Load program in the allocated memory
	if(OperatingSystem_LoadProgram(programFile, loadingPhysicalAddress, processSize) == TOOBIGPROCESS) {
		return TOOBIGPROCESS;
	}
    //...Código restante
}

-----------------------------
B) No es necesario, parte del 8b
-----------------------------

==================================================
Ejercicio 10
==================================================

La opción  --initialPID=3 hace que el proceso SystemIdleProcess se cargue con el PID 3. Sirve para comprobar que el SO funciona sin identificar a este proceso por su PID de manera hardcodeada.

Parte de la función modificada:

// Initial set of tasks of the OS
void OperatingSystem_Initialize(int programsFromFileIndex) {
	
	int i, selectedProcess;
	
// In this version, with original configuration of memory size (300) and number of processes (4)
// every process occupies a 60 positions main memory chunk 
// and OS code and the system stack occupies 60 positions 

	OS_address_base = MAINMEMORYSIZE - OS_MEMORY_SIZE;

	MAINMEMORYSECTIONSIZE = OS_address_base / PROCESSTABLEMAXSIZE;

	// Modified for exercise 10
	// If the initial PID is not assigned via command line options, select the last position of the Process Table as PID
	if (initialPID<0)
		initialPID=PROCESSTABLEMAXSIZE -1; 

//Más código
}