/*
 * ControlBoard.h
 *
 *  Created on: Oct. 14, 2021
 *      Author: lvoze
 */

#ifndef INC_CONTROLBOARD_H_
#define INC_CONTROLBOARD_H_

#include "UJA1075.h"
#include <SerialCommands.h>

#include "cmsis_os.h"

//Message struct parameter
#define MSG_ENABLED 1
#define MSG_DISABLED 0

//CAN Output Definitions
#define CAN_TXFRAME_ID 0x200
#define CAN_TXFRAME0_SHUTDOWN 1
#define CAN_TXFRAME0_BIT2 1<<1

#define UART_INIT_CHAR '$'

typedef struct
{
	CAN_HandleTypeDef * CAN_Handle;
	UART_HandleTypeDef * UART_Handle;

	GPIO_TypeDef * LED1_GPIO_Port;
	uint32_t LED1_GPIO_Pin;

	GPIO_TypeDef * LED2_GPIO_Port;
	uint32_t LED2_GPIO_Pin;

	osSemaphoreId_t * ProcessCommandSemaphore_Handle;

	UJA1075_Handle SBC_Handle;
} ControlBoardHardware;

typedef struct
{
	uint32_t id;
	uint8_t  bit;
	uint8_t length;
	int32_t value;
	uint8_t enabled;
} CAN_Message_Typedef;

//Define default filter array used on startup
const CAN_Message_Typedef defaultMessageArray[16] =
{
		{ 0x360,   0,  16,   -1,  MSG_ENABLED  },  //Engine RPM
		{ 0x360,  32,  16,   -1,  MSG_ENABLED  },  //Throttle Position

		{ 0x361,  16,  16,   -1,  MSG_ENABLED  },  //Oil Pressure

		{ 0x3E0,   0,  16,   -1,  MSG_ENABLED  },  //Coolant Temperature

		{ 0x390,   0,  16,   -1,  MSG_ENABLED  },  //Brake Pressure
		{ 0x390,   0,  16,   -1,  MSG_ENABLED  },  //Brake Bias
		{ 0x390,   0,  16,   -1,  MSG_ENABLED  },  //Lat Accel
		{ 0x390,   0,  16,   -1,  MSG_ENABLED  },  //Long Accel

		{ 0x370,   0,  16,   -1,  MSG_ENABLED  },  //GPS Speed

		{ 0x3E0,   48,  16,   -1,  MSG_ENABLED },  //Oil Temperature

		{ 0x373,   0,  16,   -1,  MSG_ENABLED  },  //EGT 1

		{ 0x368,   0,  16,   -1,  MSG_ENABLED  },  //Wideband

		{ 0x3EB,  32,  16,   -1,  MSG_ENABLED  },  //Ignition Angle

		{     0,   0,   0,   -1,  MSG_DISABLED },  //Disabled
		{     0,   0,   0,   -1,  MSG_DISABLED },  //Disabled
		{     0,   0,   0,   -1,  MSG_DISABLED }   //Disabled
};

/**
 * @brief Initializes control board state and hardware
 *
 * @param handle
 */
void InitControlboard(ControlBoardHardware * handle);

/**
 * @brief Procedurally generates and sets CAN Filter configurations from the message[] struct array config
 *
 *
 * @param handle
 * @param messageArray
 * @param size
 */
void ConfigureCANFilters(ControlBoardHardware * handle, CAN_Message_Typedef * messageArray, uint8_t size);

/**
 * @brief Clears all values in the CAN message array
 *
 */
void ClearCANValues(void);

/**
 * @brief Initializes the CAN hardware
 *
 * @param handle
 */
void Init_CAN(ControlBoardHardware * handle);

/**
 * @brief Task responsible for sending CAN frames
 *
 * @param handle
 */
void SendCANFramesTask(ControlBoardHardware * handle);

/**
 * @brief Task responsible for processing commands over UART
 *
 * @param handle
 */
void ProcessCommandTask(ControlBoardHardware * handle);

/**
 * @brief Task responsible for sending the telemetry data to UART
 *
 * @param handle
 */
void SendTelemetryTask(ControlBoardHardware * handle);

/**
 * @brief Task responsible for feeding watchdog
 *
 * @param handle
 */
void FeedWatchdogTask(ControlBoardHardware * handle);

/**
 * @brief UART RX ISR handler
 *
 * @param handle
 */
void UART_RX_ISR(ControlBoardHardware * handle);

/**
 * @brief CAN RX ISR handler
 *
 * @param hcan
 */
void CAN_RX_ISR(CAN_HandleTypeDef *hcan);

#endif /* INC_CONTROLBOARD_H_ */
