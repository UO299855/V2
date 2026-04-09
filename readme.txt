================================================================================
AVISO IMPORTANTE
================================================================================

Se recomienda ENCARECIDAMENTE leer el PDF original en lugar de este archivo,
ya que el formato PDF preserva mejor el codigo fuente, las trazas de terminal,
la tipografia y la estructura visual del documento. Este archivo .txt es
unicamente una alternativa de consulta rapida en texto plano.

Los contenidos de este archivo son los mismos que los del PDF.

Nota del PDF: En este documento se muestran ejemplos de salida de terminal.
Las indentaciones de estos ejemplos pueden diferir ligeramente de la salida
real del simulador (solo a nivel estetico).

================================================================================
SISTEMAS OPERATIVOS
Ejercicios de la version V2
Javier Ortin Rodenas
01/04/2026
================================================================================

================================================================================
1. EJERCICIO 1
================================================================================

a) Asignar el bit 9 de interrupcion para el reloj

    // Ex1: modification
    enum INT_BITS {SYSCALL_BIT=2, EXCEPTION_BIT=6, CLOCKINT_BIT=9};

b) Crear HandleClockInterrumpt y su prototipo

Basta anadir el siguiente prototipo al principio de OperatingSystem.c:

    // Ex1: modification
    void OperatingSystem_HandleClockInterrupt();

c) Modifica el sistema para que la funcion anterior atienda las
   interrupciones de reloj

Cuando se produce una interrupcion del tipo i-esimo, se modifica el registro
contador de programa para que apunte a la rutina de interrupcion adecuada. Tal
y como esta hecho nuestro SO, esto se hace inicializando la tabla de vectores de
interrupcion para que cada tipo de interrupcion apunte a una zona del codigo del
sistema operativo.

Comencemos modificando el codigo del sistema operativo. Ahora, este sera el
codigo del archivo OperatingSystemCode:

    11
    IRET // Initial Operation for OS
    HALT // Shutdown the System
    // Here interrupt vector
    OS 2 // SysCall Interrupt
    IRET
    OS 6 // Exception Interrupt
    IRET
    // Custom interrupt handlers
    OS 9 // Ex 1: Clock Interrupt
    IRET

Para que esta modificacion sea efectiva, necesitamos que al tratar una
interrupcion del tipo 9 (reloj), el contador de programa apunte a la linea de
codigo que buscamos. Para ello, hemos de modificar como se inicializa la tabla:

    // Initialization of the interrupt vector table
    void Processor_InitializeInterruptVectorTable(int interruptVectorInitialAddress) {
        int i;
        for (i=0; i< INTERRUPTTYPES;i++) { // Inicialice all to inicial IRET
            interruptVectorTable[i]=interruptVectorInitialAddress-2;
        }

        interruptVectorTable[SYSCALL_BIT]=interruptVectorInitialAddress;
            // SYSCALL_BIT=2
        interruptVectorTable[EXCEPTION_BIT]=interruptVectorInitialAddress
            +NUMBER_OF_CPU_INSTRUCTIONS_PER_INTERRUPT;

        // Ex 1: modification
        // EXCEPTION_BIT=9
        interruptVectorTable[CLOCKINT_BIT]=interruptVectorInitialAddress
            + 2*NUMBER_OF_CPU_INSTRUCTIONS_PER_INTERRUPT;
    }

Actualmente, cuando se produzca una interrupcion de tipo 9, el sistema ejecutara
las ordenes OS 9 y a continuacion IRET. Por ultimo, hemos de hacer que el
manejador OS 9 quede asociado a la funcion OperatingSystem_HandleClockInterrumpt.

    void OperatingSystem_InterruptLogic(int entryPoint){
        switch (entryPoint){
        case SYSCALL_BIT: // SYSCALL_BIT=2
            OperatingSystem_HandleSystemCall();
            break;
        case EXCEPTION_BIT: // EXCEPTION_BIT=6
            OperatingSystem_HandleException();
            break;
        // Ex 1: modification
        case CLOCKINT_BIT: //CLOCKINT_BIT=9
            OperatingSystem_HandleClockInterrupt();
            break;
        }
    }

d) Modificar Clock_Update para que produzca interrupciones de reloj

    // Ex 1: modification
    void Clock_Update() {
        if(++tics%intervalBetweenInterrupts == 0) {
            Processor_RaiseInterrupt(CLOCKINT_BIT);
        }
    }

e) Comprobar que se detenga la ejecucion con puntos de depuracion

El cuerpo de la funcion OperatingSystem_HandleClockInterrupt es el siguiente:

    void OperatingSystem_HandleClockInterrupt() {
        numberOfClockInterrupts++;
        ComputerSystem_DebugMessage(TIMED_MESSAGE, 57, INTERRUPT,
            numberOfClockInterrupts);
        return;
    }

Podemos ver como se detiene la ejecucion cuando usamos breakpoints en modo
depuracion.

f) Anadir funcionalidad a OperatingSystem_HandleClockInterrupt

Los cambios pueden verse en el codigo del apartado anterior.


================================================================================
2. EJERCICIO 2
================================================================================

a) Anadir el bit de enmascaramiento a la PSW

    // [In Processor.h]
    enum PSW_BITS {POWEROFF_BIT=0, ZERO_BIT=1,
                   NEGATIVE_BIT=2, OVERFLOW_BIT=3, EXECUTION_MODE_BIT=7,
                   // Ex 2: modification
                   INTERRUPT_MASKED_BIT=15};

c) Modificar Processor_ShowPSW

    // Ex 2: modification
    char * Processor_ShowPSW(){
        strcpy(pswmask,"----------------");
        int tam=strlen(pswmask)-1;
        if (Processor_PSW_BitState(EXECUTION_MODE_BIT))
            pswmask[tam-EXECUTION_MODE_BIT]='X';
        if (Processor_PSW_BitState(OVERFLOW_BIT))
            pswmask[tam-OVERFLOW_BIT]='F';
        if (Processor_PSW_BitState(NEGATIVE_BIT))
            pswmask[tam-NEGATIVE_BIT]='N';
        if (Processor_PSW_BitState(ZERO_BIT))
            pswmask[tam-ZERO_BIT]='Z';
        if (Processor_PSW_BitState(POWEROFF_BIT))
            pswmask[tam-POWEROFF_BIT]='S';

        // Ex 2: Masked interruptions
        if (Processor_PSW_BitState(INTERRUPT_MASKED_BIT))
            pswmask[tam-INTERRUPT_MASKED_BIT]='M';
        return pswmask;
    }

d) Hacer que solo se traten las interrupciones cuando no estan enmascaradas

    void Processor_ManageInterrupts() {

        int i;
        // Ex 2: Only check as long as interrupts are not masked
        for (i=0;!Processor_PSW_BitState(INTERRUPT_MASKED_BIT) &&
                i<INTERRUPTTYPES;i++)
            if (Processor_GetInterruptLineStatus(i)) {
                Processor_ACKInterrupt(i);
                Processor_PushInSystemStack(registerPC_CPU);
                Processor_PushInSystemStack(registerPSW_CPU);
                Processor_ActivatePSW_Bit(INTERRUPT_MASKED_BIT);
                Processor_ActivatePSW_Bit(EXECUTION_MODE_BIT);
                registerPC_CPU=interruptVectorTable[i];
            }
    }

Comprobacion: Veamos que todas las modificaciones de los dos ejercicios
funcionan. Si ejecutamos un programa muy simple (solo hace ADD 1 0 muchas veces
hasta finalmente hacer TRAP 3), obtenemos:

    $ ./Simulator --debugsections=HD,INTERRUPT prog1

    [0] User programs list:
    Program [prog1] with arrival time [0]
    [0] Process [3] created into the [NEW] state, from program [SystemIdleProcess]
    [0] Process [3 - SystemIdleProcess] moving from the [NEW] state to the [READY] state
    [0] Process [0] created into the [NEW] state, from program [prog1]
    [0] Process [0 - prog1] moving from the [NEW] state to the [READY] state
    [0] Process [0 - prog1] moving from the [READY] state to the [EXECUTING] state
    [1] 0D 000 000 IRET 0 0 (PID: 0, PC: 0, Accumulator: 0, PSW: 0002
        [--------------Z-], IntLine: [0000])
    [2] 01 001 000 ADD 1 0 (PID: 0, PC: 1, Accumulator: 1, PSW: 0000
        [----------------], IntLine: [0000])
    [3] 01 001 000 ADD 1 0 (PID: 0, PC: 2, Accumulator: 1, PSW: 0000
        [----------------], IntLine: [0000])
    [4] 01 001 000 ADD 1 0 (PID: 0, PC: 3, Accumulator: 1, PSW: 0000
        [----------------], IntLine: [0000])
    [5] 01 001 000 ADD 1 0 (PID: 0, PC: 4, Accumulator: 1, PSW: 0000
        [----------------], IntLine: [0200])
    [6] 0C 009 000 OS 9 0 (PID: 0, PC: 246, Accumulator: 1, PSW: 8080
        [M-------X-------], IntLine: [0000])
    [7] Clock interrupt number [1] has occurred
    [8] 0D 000 000 IRET 0 0 (PID: 0, PC: 4, Accumulator: 1, PSW: 0000
        [----------------], IntLine: [0000])
    [9] 01 001 000 ADD 1 0 (PID: 0, PC: 5, Accumulator: 1, PSW: 0000
        [----------------], IntLine: [0000])
    [10] 01 001 000 ADD 1 0 (PID: 0, PC: 6, Accumulator: 1, PSW: 0000
         [----------------], IntLine: [0200])
    //... Resto de la ejecucion...
    $

Podemos observar como el manejador de interrupciones es el apropiado, que cumple
su funcion. Ademas, la PSW se imprime adecuadamente al iniciar el tratamiento de
interrupciones, enmascarando el resto.


================================================================================
3. EJERCICIO 3
================================================================================

a) Al final de la inicializacion del SO

    // Initial set of tasks of the OS
    void OperatingSystem_Initialize(int programsFromFileIndex) {
        // [...Rest of the code...]
        // Ex 3: modification
        OperatingSystem_PrintStatus();
    }

b) En SyscallYield solo si se cambia de proceso

    void OperatingSystem_HandleYield() {
        int currentQueue = processTable[executingProcessID].queueID;
        int otherProcessID = Heap_getFirst(readyToRunQueue[currentQueue],
            numberOfReadyToRunProcesses[currentQueue]);
        if(otherProcessID != -1 && processTable[executingProcessID].priority ==
                processTable[otherProcessID].priority) {
            // yielding is possible
            ComputerSystem_DebugMessage(TIMED_MESSAGE, 55, SHORTTERMSCHEDULE,
                executingProcessID,
                programList[processTable[executingProcessID].programListIndex]
                    ->executableName,
                otherProcessID,
                programList[processTable[otherProcessID].programListIndex]
                    ->executableName);
            OperatingSystem_ExtractFromReadyToRunQueue(currentQueue);
            OperatingSystem_PreemptRunningProcess();
            OperatingSystem_Dispatch(otherProcessID);

            // Ex 3: modification
            OperatingSystem_PrintStatus();

        } else {
            // yielding is not possible
            ComputerSystem_DebugMessage(TIMED_MESSAGE, 56, SHORTTERMSCHEDULE,
                executingProcessID,
                programList[processTable[executingProcessID].programListIndex]
                    ->executableName);
        }
    }

c) Como ultima sentencia de SYSCALL_END

    void OperatingSystem_HandleSystemCall() {
        int systemCallID;
        systemCallID=Processor_GetRegisterC();

        switch (systemCallID) {
        case SYSCALL_END:
            // Show message: "Process [executingProcessID] has requested to
            //   terminate\n"
            ComputerSystem_DebugMessage(TIMED_MESSAGE,73,SYSPROC,
                executingProcessID,
                programList[processTable[executingProcessID].programListIndex]
                    ->executableName);
            OperatingSystem_TerminateExecutingProcess();

            // Ex 3: modification
            OperatingSystem_PrintStatus();
            break;

        //...Rest of the code...
        }
    }

d) Como ultima sentencia del manejador de excepciones

    // Exception management routine
    void OperatingSystem_HandleException() {
        ComputerSystem_DebugMessage(TIMED_MESSAGE,71,INTERRUPT,
            executingProcessID,
            programList[processTable[executingProcessID].programListIndex]
                ->executableName);

        OperatingSystem_TerminateExecutingProcess();
        // Ex 3: modification
        OperatingSystem_PrintStatus();
    }

e) Al final del planificador a largo plazo, solo si se ha creado un proceso
   en su ejecucion

    int OperatingSystem_LongTermScheduler() {

        int createdProcessPID, i,
        numberOfSuccessfullyCreatedProcesses=0;

        while (OperatingSystem_IsThereANewProgram()!=EMPTYQUEUE) {
            i=Heap_poll(arrivalTimeQueue,QUEUE_ARRIVAL,
                &numberOfProgramsInArrivalTimeQueue);
            createdProcessPID=OperatingSystem_CreateProcess(i);
            switch (createdProcessPID) {
            //... Rest of (unsuccessful) cases...
            default:
                // Process creation has succeeded: additional actions
                ComputerSystem_DebugMessage(TIMED_MESSAGE,54,SYSPROC,
                    createdProcessPID,
                    statesNames[NEW],programList[i]->executableName);
                numberOfSuccessfullyCreatedProcesses++;
                if (programList[i]->type==USERPROGRAM)
                    numberOfNotTerminatedUserProcesses++;
                // Move process to the ready state
                OperatingSystem_MoveToTheREADYState(createdProcessPID);

                // Ex 3: modification
                OperatingSystem_PrintStatus();
                break;
            }
        }
        // Return the number of succesfully created
        return numberOfSuccessfullyCreatedProcesses;
    }


================================================================================
4. EJERCICIO 4
================================================================================

    void OperatingSystem_MoveToTheREADYState(int PID) {
        int processQueueID = processTable[PID].queueID;
        if (Heap_add(PID, readyToRunQueue[processQueueID],QUEUE_PRIORITY,
                &(numberOfReadyToRunProcesses[processQueueID]))>=0) {

            ComputerSystem_DebugMessage(TIMED_MESSAGE, 53, SYSPROC, PID,
                programList[processTable[PID].programListIndex]->executableName,
                statesNames[processTable[PID].state], statesNames[READY]);
            // Change of state
            processTable[PID].state=READY;
        }
        // Ex 4: modification
        //OperatingSystem_PrintReadyToRunQueue();
    }

    void OperatingSystem_Dispatch(int PID) {
        // The process identified by PID becomes the current executing process
        executingProcessID=PID;
        ComputerSystem_DebugMessage(TIMED_MESSAGE, 53, SYSPROC, PID,
            programList[processTable[PID].programListIndex]->executableName,
            statesNames[processTable[PID].state], statesNames[EXECUTING]);
        // Change the process' state
        processTable[PID].state=EXECUTING;
        // Ex 4:
        //OperatingSystem_PrintReadyToRunQueue();
        // Modify hardware registers with appropriate values for the process
        // identified by PID
        OperatingSystem_RestoreContext(PID);
    }


================================================================================
5. EJERCICIO 5
================================================================================

a) Nuevo campo del PCB

    typedef struct {
        //...Rest of fields...

        // Ex 5: modifications
        int whenToWakeUp;
    } PCB;

b) Cola de procesos dormidos

    // [OperatingSystem.c]
    // Ex 5: Heap with blocked processes, sorted by when-to-wakeup
    heapItem *sleepingProcessesQueue;
    int numberOfSleepingProcesses=0;

Reservamos espacio para la cola e iniciamos el campo whenToWakeUp anterior segun
el convenio establecido.

    void OperatingSystem_Initialize(int programsFromFileIndex) {
        //...Previous code...

        // Ex 5: modification, create sleeping queue
        sleepingProcessesQueue = Heap_create(PROCESSTABLEMAXSIZE);

        // Load Operating System Code
        OperatingSystem_LoadOperatingSystemCode(OPERATING_SYSTEM_CODE_FILE,
            OS_address_base);

        // Process table initialization (all entries are free)
        for (i=0; i<PROCESSTABLEMAXSIZE;i++){
            //...Rest of the fields...

            // Ex 5: modification
            processTable[i].whenToWakeUp = -1;
        }
        //...Rest of the function...
    }

c) Definir SLEEPINGQUEUE

    //[OperatingSystem.h]
    // Ex 5: modification
    #define SLEEPINGQUEUE

d) Definir un registro D

    // [Processor.c]
    // Ex 5: modification
    int registerD_CPU;
    //...Rest of the file...
    int Processor_GetRegisterD() {
        return registerD_CPU;
    }

    void Processor_SetRegisterD(int value) {
        registerD_CPU = value;
    }

    // [Processor.h]
    //Ex 5: modifications
    int Processor_GetRegisterD();
    void Processor_SetRegisterD(int);

e) Modificar la instruccion TRAP para guardar su segundo operando en
   el registro D al ejecutarse

    void Processor_DecodeAndExecuteInstruction() {
        //...Previous code..
        switch (operationCode) {

        //...Rest of the cases...

        case TRAP_INST:
            // Ex 5: save operand 2 on D register
            Processor_SetRegisterD(operand2);
            Processor_RaiseInterrupt(SYSCALL_BIT);
            registerC_CPU=operand1;
            registerPC_CPU++;
            break;
        }

        //...Rest of the code...
    }

f) Anadir una llamada SYSCALL_SLEEP

En primer lugar, hemos de definir la constante apropiadamente:

    //[OperatingSystem.h]
    // Ex 5: modification (SYSCALL_SLEEP)
    enum SystemCallIdentifiers {
        SYSCALL_END=3,
        SYSCALL_YIELD=4,
        SYSCALL_PRINTEXECINFO=5,
        SYSCALL_SLEEP=7}; //Modification

Ahora, hemos de crear un manejador para este tipo de llamada al sistema. En
primer lugar, creamos una funcion vacia e incluimos el prototipo al inicio del
archivo. Ademas, hemos de referenciar a esta funcion como responsable del manejo
de TRAP 7:

    //[OperatingSystem.c]
    //Ex 5: modification
    void OperatingSystem_HandleSleep();

    //...Code gap...
    void OperatingSystem_HandleSystemCall() {
        int systemCallID;
        // Register C contains the identifier of the issued system call
        systemCallID=Processor_GetRegisterC();

        switch (systemCallID) {
        //...Other cases...
        // Ex 5: modification
        case SYSCALL_SLEEP:
            OperatingSystem_HandleSleep();
            break;
        }
    }

    //...Code gap...
    void OperatingSystem_HandleSleep(){}

Ahora queda establecer el comportamiento del manejador:

    // Ex 5: modification
int OperatingSystem_MoveToTheBLOCKEDState(int PID) {
	// When to wake up
	processTable[executingProcessID].whenToWakeUp = 1 + numberOfClockInterrupts +
				((Processor_GetRegisterD() > 0) ? Processor_GetRegisterD() :
					abs(Processor_GetAccumulator()));
	if (Heap_add(PID, sleepingProcessesQueue,QUEUE_WAKEUP ,&(numberOfSleepingProcesses))>=0) {
		// Saving context
		OperatingSystem_SaveContext(executingProcessID);

		// Logging the state change
		ComputerSystem_DebugMessage(TIMED_MESSAGE, 53, SYSPROC, PID,
			programList[processTable[PID].programListIndex]->executableName,
			statesNames[processTable[PID].state], statesNames[BLOCKED]);			
		//  Change of state
		processTable[PID].state=BLOCKED;		
		return 0;
	}
	return -1;
}

    // Ex5: modification
    void OperatingSystem_HandleSleep() {
        //Only if we can add it to the appropriate heap
        if (!OperatingSystem_MoveToTheBLOCKEDState(executingProcessID)) {
            executingProcessID = NOPROCESS;
            OperatingSystem_Dispatch(OperatingSystem_ShortTermScheduler());
            OperatingSystem_PrintStatus();
        }
        return;
    }

    Importante: En este caso, tenemos que asignar el campo whenToWakeUp al
proceso antes de insertarlo en la cola de dormidos, pues al a˜nadirlo al heap cor-
respondiente se ordenar´an seg´un el valor de este campo. De no hacer este ajuste,
como whenToWakeUp se inicializa por defecto a -1, el último proceso insertado iría
siempre al inicio del montículo, incluso si tendr´ıa que despertarse m´as tarde.

g) Imprimir el estado del sistema

Puede verse en el codigo anterior.

h) Seguir los criterios del ejercicio 0

Puede verse en el codigo del apartado (b).

--------------------------------------------------------------------------------
Prueba de funcionamiento
--------------------------------------------------------------------------------

Programa de prueba (programSleep):

    10 //programSleep
    3
    ADD -5 0
    TRAP 7 -2
    TRAP 3

Actualmente, podemos dormir procesos, pero no despertarlos. Probemos el
funcionamiento actual del simulador con un programa de prueba.

Si ejecutamos el programa anterior:

    $ ./Simulator --debugSections=HD,INTERRUPT,SHORTTERMSCHEDULE programSleep | head -n 100

    48 messages loaded from file messagesTCH.txt
    6 messages loaded from file messagesSTD.txt
    0 Asserts Loaded
    [0] STARTING simulation
    [0] User programs list:
    Program [programSleep] with arrival time [0]
    [0] Arrival Time Queue:
    [SystemIdleProcess, 0, DAEMON-PROGRAM]
    [programSleep, 0, USER-PROGRAM]
    [0] Process [3] created into the [NEW] state, from program [SystemIdleProcess]
    [0] Process [3 - SystemIdleProcess] moving from the [NEW] state to the [READY] state
    [0] Running Process Information:
    [--- No running process ---]
    [0] Ready-to-run process queue:
    HIGHPRIOUSER:
    LOWPRIOUSER:
    DAEMONS: [3,100]
    [0] SLEEPING Queue:
    [--- empty queue ---]
    [0] PID association with program's name:
    PID: 3 -> SystemIdleProcess
    [0] Process [0] created into the [NEW] state, from program [programSleep]
    [0] Process [0 - programSleep] moving from the [NEW] state to the [READY] state
    [0] Running Process Information:
    [--- No running process ---]
    [0] Ready-to-run process queue:
    HIGHPRIOUSER: [0,3]
    LOWPRIOUSER:
    DAEMONS: [3,100]
    [0] SLEEPING Queue:
    [--- empty queue ---]
    [0] PID association with program's name:
    PID: 0 -> programSleep
    PID: 3 -> SystemIdleProcess
    [0] Process [0 - programSleep] moving from the [READY] state to the [EXECUTING] state
    [0] Running Process Information:
    [PID: 0, Priority: 3, WakeUp: 0, Queue: HIGHPRIOUSER]
    [0] Ready-to-run process queue:
    HIGHPRIOUSER:
    LOWPRIOUSER:
    DAEMONS: [3,100]
    [0] SLEEPING Queue:
    [--- empty queue ---]
    [0] PID association with program's name:
    PID: 0 -> programSleep
    PID: 3 -> SystemIdleProcess
    [1] 0D 000 000 IRET 0 0 (PID: 0, PC: 0, Accumulator: 0, PSW: 0002
        [--------------Z-], IntLine: [0000])
    [2] 01 805 000 ADD -5 0 (PID: 0, PC: 1, Accumulator: -5, PSW: 0004
        [-------------N--], IntLine: [0000])
    [3] 04 007 802 TRAP 7 -2 (PID: 0, PC: 2, Accumulator: -5, PSW: 0004
        [-------------N--], IntLine: [0004])
    [4] 0C 002 000 OS 2 0 (PID: 0, PC: 242, Accumulator: -5, PSW: 8084
        [M-------X----N--], IntLine: [0000])
    [5] Process [0 - programSleep] moving from the [EXECUTING] state to the [BLOCKED]
        state
    [5] Process [3 - SystemIdleProcess] moving from the [READY] state to the
        [EXECUTING] state
    [5] Running Process Information:
    [PID: 3, Priority: 100, WakeUp: 0, Queue: DAEMONS]
    [5] Ready-to-run process queue:
    HIGHPRIOUSER:
    LOWPRIOUSER:
    DAEMONS:
    [5] SLEEPING Queue:
    [0, 3, 6]
    [5] PID association with program's name:
    PID: 0 -> programSleep
    PID: 3 -> SystemIdleProcess
    [6] 0D 000 000 IRET 0 0 (PID: 3, PC: 180, Accumulator: 0, PSW: 0082
        [--------X-----Z-], IntLine: [0200])
    [7] 0C 009 000 OS 9 0 (PID: 3, PC: 246, Accumulator: 0, PSW: 8082
        [M-------X-----Z-], IntLine: [0000])
    [8] Clock interrupt number [1] has occurred
    [9] 0D 000 000 IRET 0 0 (PID: 3, PC: 180, Accumulator: 0, PSW: 0082
        [--------X-----Z-], IntLine: [0000])
    [10] 01 5E2 398 ADD 1506 920 (PID: 3, PC: 181, Accumulator: 2426, PSW: 0080
         [--------X-------], IntLine: [0200])
    [11] 0C 009 000 OS 9 0 (PID: 3, PC: 246, Accumulator: 2426, PSW: 8080
         [M-------X-------], IntLine: [0000])
    [12] Clock interrupt number [2] has occurred
    // ... (continua de igual manera hasta el tick 42) ...
    [42] Clock interrupt number [8] has occurred
    $

Podemos ver como actualmente se cede la CPU al proceso inactivo del sistema,
pero el proceso del usuario nunca la recupera, incluso aun pasando el numero de
interrupciones de reloj necesarias para ello. Hemos de implementar algun
mecanismo para "despertar" a los procesos dormidos.


================================================================================
6. EJERCICIO 6
================================================================================

a) Comprobar el campo whenToWakeUp de los procesos dormidos al manejar
   interrupciones de reloj

Desde OperatingSystem_HandleClockInterrumpt llamaremos a la siguiente funcion,
que comprueba si existen procesos a despertar. En tal caso, los pasa a la cola
de listos pertinente en cada caso.

    int OperatingSystem_CheckProcessesToWakeUp() {
        int foundAny = 0, checking = 1, sleepingPID;
        while(checking) {
            // Check if there are asleep processes and/or if they are due for
            // being awoken
            if(((sleepingPID=Heap_getFirst(sleepingProcessesQueue,
                    numberOfSleepingProcesses))!=-1)
                    && processTable[sleepingPID].whenToWakeUp ==
                    numberOfClockInterrupts) {
                // A process needs to wake up
                Heap_poll(sleepingProcessesQueue, QUEUE_WAKEUP,
                    &numberOfSleepingProcesses);
                OperatingSystem_MoveToTheREADYState(sleepingPID);
                foundAny = 1;
            } else { // No more asleep processes or they need to sleep for longer
                checking = 0;
            }
        }
        return foundAny;
    }

c) Comprobar si el proceso en ejecucion sigue siendo el mas adecuado

Desde OperatingSystem_HandleClockInterrumpt tambien llamaremos a la siguiente
funcion:

   // Ex 6: modification
    int OperatingSystem_CheckForHigherPriority() {
        int maxQueue = processTable[executingProcessID].queueID;
        for(int queue = 0; queue <= maxQueue; queue++) {
            int firstPID = Heap_getFirst(readyToRunQueue[queue], numberOfReadyToRunProcesses[queue]);
            if(firstPID != -1 && (queue < maxQueue ||
                processTable[firstPID].priority < processTable[executingProcessID].priority)) {
                // A more important process was found
                ComputerSystem_DebugMessage(TIMED_MESSAGE, 58, SHORTTERMSCHEDULE, executingProcessID,
                programList[processTable[executingProcessID].programListIndex]->executableName,
                firstPID,
                programList[processTable[firstPID].programListIndex]->executableName);
                OperatingSystem_ExtractFromReadyToRunQueue(queue);
                OperatingSystem_PreemptRunningProcess();
                OperatingSystem_Dispatch(firstPID);
                return 1;
            }
        }
    return 0;
    }

    Importante: no basta con mirar todas las colas y cambiar siempre que encontremos un
proceso con menor campo de prioridad (m´as prioritario). Hemos de respetar el orden de
las colas de prioridad. Analizamos todas las colas hasta llegar a la del proceso que
está en ejecucón. Un proceso se considera m´as importante
que el que se está ejecutando si tiene un queueID menor (está en una cola más
prioritaria) o si pertenece a la misma cola que el proceso en ejecución y tiene menor
campo priority (más prioritario).


b) Imprimir el estado del sistema una vez se procese la cola de dormidos,
   en caso de haber desbloqueado un proceso

Asi es como queda la funcion OperatingSystem_HandleClockInterrumpt con las
modificaciones pertinentes:

    void OperatingSystem_HandleClockInterrupt() {
        numberOfClockInterrupts++;
        ComputerSystem_DebugMessage(TIMED_MESSAGE, 57, INTERRUPT,
            numberOfClockInterrupts);
        // Ex 6: modification
        if(OperatingSystem_CheckProcessesToWakeUp()) {
            OperatingSystem_PrintStatus();
            if(OperatingSystem_CheckForHigherPriority()) {
                OperatingSystem_PrintStatus();
            }
        }
        return;
    }

Notese que la llamada a OperatingSystem_PrintStatus esta dentro del primer if,
asi que solo se imprimira en caso de haber desbloqueado al menos un proceso.
Ademas, en caso de haber salida por consola, solo se imprimira el estado una
unica vez, en lugar de hacerlo para cada proceso desbloqueado (siguiendo el
comportamiento deseable).

d) Imprimir el estado del sistema si se cambia el proceso en ejecucion

Notese una llamada a OperatingSystem_PrintStatus en el segundo if del apartado
anterior. Asi, solo se imprime la informacion en caso de haber cambiado el
proceso en ejecucion.

Como nota adicional, cuando llamamos al Dispatcher, se restaura el contexto del
proceso que pasa a ejecucion. Por tanto, es muy importante haber guardado el
contexto en el codigo de MoveToTheBLOCKEDState: apartado (f) del ejercicio 5.

--------------------------------------------------------------------------------
Prueba de funcionamiento
--------------------------------------------------------------------------------

Programa de prueba (programSleep):

    10 //programSleep
    3
    ADD -5 0
    TRAP 7 -2
    TRAP 3

Ejecutemos ahora el mismo programa de prueba que para el ejercicio 5, para
comprobar que se despierta al proceso dormido adecuadamente.

    $ ./Simulator programSleep

    [...Initialization...]

    [1] 0D 000 000 IRET 0 0 (PID: 0, PC: 0, Accumulator: 0, PSW: 0002 [--------------Z-],
    IntLine: [0000])
    [2] 01 805 000 ADD -5 0 (PID: 0, PC: 1, Accumulator: -5, PSW: 0004 [-------------N--],
    IntLine: [0000])
    [3] 04 007 802 TRAP 7 -2 (PID: 0, PC: 2, Accumulator: -5, PSW: 0004 [-------------N--],
    IntLine: [0004])
    [4] 0C 002 000 OS 2 0 (PID: 0, PC: 242, Accumulator: -5, PSW: 8084 [M-------X----N--],
    IntLine: [0000])
    [5] Process [0 - programSleep] moving from the [EXECUTING] state to the [BLOCKED] state
    [5] Process [3 - SystemIdleProcess] moving from the [READY] state to the [EXECUTING]
    state
    [5] Running Process Information:
    [PID: 3, Priority: 100, WakeUp: -1, Queue: DAEMONS]
    [5] Ready-to-run process queue:
    HIGHPRIOUSER:
    LOWPRIOUSER:
    DAEMONS:
    [5] SLEEPING Queue:
    [0, 3, 6]
    [5] PID association with program’s name:
    PID: 0 -> programSleep
    PID: 3 -> SystemIdleProcess
    [6] 0D 000 000 IRET 0 0 (PID: 3, PC: 180, Accumulator: 0, PSW: 0082 [--------X-----Z-],
    IntLine: [0200])
    [7] 0C 009 000 OS 9 0 (PID: 3, PC: 246, Accumulator: 0, PSW: 8082 [M-------X-----Z-],
    IntLine: [0000])
    [8] Clock interrupt number [1] has occurred
    [9] 0D 000 000 IRET 0 0 (PID: 3, PC: 180, Accumulator: 0, PSW: 0082 [--------X-----Z-],
    IntLine: [0000])
    [10] 01 5E2 398 ADD 1506 920 (PID: 3, PC: 181, Accumulator: 2426, PSW: 0080
    [--------X-------], IntLine: [0200])
    [11] 0C 009 000 OS 9 0 (PID: 3, PC: 246, Accumulator: 2426, PSW: 8080 [M-------X-------],
    IntLine: [0000])
    [12] Clock interrupt number [2] has occurred
    [13] 0D 000 000 IRET 0 0 (PID: 3, PC: 181, Accumulator: 2426, PSW: 0080
    [--------X-------], IntLine: [0000])
    [14] 05 000 000 NOP 0 0 (PID: 3, PC: 182, Accumulator: 2426, PSW: 0080 [--------X-------],
    IntLine: [0000])
    [15] 06 801 000 JUMP -1 0 (PID: 3, PC: 181, Accumulator: 2426, PSW: 0080
    [--------X-------], IntLine: [0200])
    [16] 0C 009 000 OS 9 0 (PID: 3, PC: 246, Accumulator: 2426, PSW: 8080 [M-------X-------],
    IntLine: [0000])
    [17] Clock interrupt number [3] has occurred
    [18] 0D 000 000 IRET 0 0 (PID: 3, PC: 181, Accumulator: 2426, PSW: 0080
    [--------X-------], IntLine: [0000])
    [19] 05 000 000 NOP 0 0 (PID: 3, PC: 182, Accumulator: 2426, PSW: 0080 [--------X-------],
    IntLine: [0000])
    [20] 06 801 000 JUMP -1 0 (PID: 3, PC: 181, Accumulator: 2426, PSW: 0080
    [--------X-------], IntLine: [0200])
    [21] 0C 009 000 OS 9 0 (PID: 3, PC: 246, Accumulator: 2426, PSW: 8080 [M-------X-------],
    IntLine: [0000])
    [22] Clock interrupt number [4] has occurred
    [23] 0D 000 000 IRET 0 0 (PID: 3, PC: 181, Accumulator: 2426, PSW: 0080
    [--------X-------], IntLine: [0000])
    [24] 05 000 000 NOP 0 0 (PID: 3, PC: 182, Accumulator: 2426, PSW: 0080 [--------X-------],
    IntLine: [0000])
    [25] 06 801 000 JUMP -1 0 (PID: 3, PC: 181, Accumulator: 2426, PSW: 0080
    [--------X-------], IntLine: [0200])
    [26] 0C 009 000 OS 9 0 (PID: 3, PC: 246, Accumulator: 2426, PSW: 8080 [M-------X-------],
    IntLine: [0000])
    [27] Clock interrupt number [5] has occurred
    [28] 0D 000 000 IRET 0 0 (PID: 3, PC: 181, Accumulator: 2426, PSW: 0080
    [--------X-------], IntLine: [0000])
    [29] 05 000 000 NOP 0 0 (PID: 3, PC: 182, Accumulator: 2426, PSW: 0080 [--------X-------],
    IntLine: [0000])
    [30] 06 801 000 JUMP -1 0 (PID: 3, PC: 181, Accumulator: 2426, PSW: 0080
    [--------X-------], IntLine: [0200])
    [31] 0C 009 000 OS 9 0 (PID: 3, PC: 246, Accumulator: 2426, PSW: 8080 [M-------X-------],
    IntLine: [0000])
    [32] Clock interrupt number [6] has occurred
    [32] Process [0 - programSleep] moving from the [BLOCKED] state to the [READY] state
    [32] Running Process Information:
    [PID: 3, Priority: 100, WakeUp: -1, Queue: DAEMONS]
    [32] Ready-to-run process queue:
    HIGHPRIOUSER: [0,3]
    LOWPRIOUSER:
    DAEMONS:
    [32] SLEEPING Queue:
    [--- empty queue ---]
    [32] PID association with program’s name:
    PID: 0 -> programSleep
    PID: 3 -> SystemIdleProcess
    [32] Process [3 - SystemIdleProcess] will be thrown out of the processor by process [0
    - programSleep]
    [32] Process [3 - SystemIdleProcess] moving from the [EXECUTING] state to the [READY]
    state
    [32] Process [0 - programSleep] moving from the [READY] state to the [EXECUTING] state
    [32] Running Process Information:
    [PID: 0, Priority: 3, WakeUp: 6, Queue: HIGHPRIOUSER]
    [32] Ready-to-run process queue:
    HIGHPRIOUSER:
    LOWPRIOUSER:
    DAEMONS: [3,100]
    [32] SLEEPING Queue:
    [--- empty queue ---]
    [32] PID association with program’s name:
    PID: 0 -> programSleep
    PID: 3 -> SystemIdleProcess
    [33] 0D 000 000 IRET 0 0 (PID: 0, PC: 2, Accumulator: -5, PSW: 0004 [-------------N--],
    IntLine: [0000])
    [34] 04 003 000 TRAP 3 0 (PID: 0, PC: 3, Accumulator: -5, PSW: 0004 [-------------N--],
    IntLine: [0004])
    [35] 0C 002 000 OS 2 0 (PID: 0, PC: 242, Accumulator: -5, PSW: 8084 [M-------X----N--],
    IntLine: [0200])
    [36] Process [0 - programSleep] has requested to terminate
    [36] Process [0 - programSleep] moving from the [EXECUTING] state to the [EXIT] state
    [36] Process [3 - SystemIdleProcess] moving from the [READY] state to the [EXECUTING]
    state
    [36] Running Process Information:
    [PID: 3, Priority: 100, WakeUp: -1, Queue: DAEMONS]
    [36] Ready-to-run process queue:
    HIGHPRIOUSER:
    LOWPRIOUSER:
    DAEMONS:
    [36] SLEEPING Queue:
    [--- empty queue ---]
    [36] PID association with program’s name:
    PID: 0 -> programSleep
    PID: 3 -> SystemIdleProcess
    [37] 0D 000 000 IRET 0 0 (PID: 3, PC: 183, Accumulator: 2426, PSW: 0080
    [--------X-------], IntLine: [0200])
    [38] 0C 009 000 OS 9 0 (PID: 3, PC: 246, Accumulator: 2426, PSW: 8080 [M-------X-------],
    IntLine: [0000])
    [39] Clock interrupt number [7] has occurred
    [40] 0D 000 000 IRET 0 0 (PID: 3, PC: 183, Accumulator: 2426, PSW: 0080
    [--------X-------], IntLine: [0200])
    [41] 0C 009 000 OS 9 0 (PID: 3, PC: 246, Accumulator: 2426, PSW: 8080 [M-------X-------],
    IntLine: [0000])
    [42] Clock interrupt number [8] has occurred
    [43] 0D 000 000 IRET 0 0 (PID: 3, PC: 183, Accumulator: 2426, PSW: 0080
    [--------X-------], IntLine: [0000])
    [44] 04 003 000 TRAP 3 0 (PID: 3, PC: 184, Accumulator: 2426, PSW: 0080
    [--------X-------], IntLine: [0004])
    [45] 0C 002 000 OS 2 0 (PID: 3, PC: 242, Accumulator: 2426, PSW: 8080 [M-------X-------],
    IntLine: [0200])
    [46] Process [3 - SystemIdleProcess] has requested to terminate
    [46] Process [3 - SystemIdleProcess] moving from the [EXECUTING] state to the [EXIT]
    state
    [46] The system will shut down now... [46] Running Process Information:
    [--- No running process ---]
    [46] Ready-to-run process queue:
    HIGHPRIOUSER:
    LOWPRIOUSER:
    DAEMONS:
    [46] SLEEPING Queue:
    [--- empty queue ---]
    [46] PID association with program’s name:
    PID: 0 -> programSleep
    PID: 3 -> SystemIdleProcess
    [47] 0D 000 000 IRET 0 0 (PID: -1, PC: 241, Accumulator: 2426, PSW: 8080
    [M-------X-------], IntLine: [0200])
    [48] 0B 000 000 HALT 0 0 (PID: -1, PC: 241, Accumulator: 2426, PSW: 8081
    [M-------X------S], IntLine: [0200])
    [48] END of the simulation

    $

Ahora sí sigue el comportamiento esperado.