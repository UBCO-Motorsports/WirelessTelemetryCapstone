/*
 * ControlBoard.h
 *
 *  Created on: Oct. 14, 2021
 *      Author: lvoze
 */

#ifndef INC_CONTROLBOARD_H_
#define INC_CONTROLBOARD_H_

#include "UJA1075.h"
#include "cmsis_os.h"

//Message struct parameter
#define MSG_ENABLED 1
#define MSG_DISABLED 0

//CAN Output Definitions
#define CAN_TXFRAME_ID 0x200
#define CAN_TXFRAME0_SHUTDOWN 1
#define CAN_TXFRAME0_BIT2 1<<1

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
 * @param handle
 */
void CAN_RX_ISR(ControlBoardHardware * handle);

#endif /* INC_CONTROLBOARD_H_ */
