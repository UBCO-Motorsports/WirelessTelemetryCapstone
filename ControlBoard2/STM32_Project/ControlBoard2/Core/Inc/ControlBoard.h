/*
 * ControlBoard.h
 *
 *  Created on: Oct. 14, 2021
 *      Author: lvoze
 */

#ifndef INC_CONTROLBOARD_H_
#define INC_CONTROLBOARD_H_

#include <UJA1075.h>
#include <SerialCommands.h>

#include "cmsis_os.h"

//Message struct parameter
#define MSG_ENABLED 1
#define MSG_DISABLED 0

//CAN Output Frame bits
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

struct message
{
	uint32_t id;
	uint8_t  bit;
	uint8_t length;
	int32_t value;
	uint8_t enabled;
};

void InitControlboard(ControlBoardHardware * handle);

void ConfigureCANFilters(ControlBoardHardware * handle, struct message * messageArray, uint8_t size);

void ClearCANBuffers(void);

void Init_CAN(ControlBoardHardware * handle);

void SendCANFramesTask(ControlBoardHardware * handle);

void ProcessCommandTask(ControlBoardHardware * handle);

void SendTelemetryTask(ControlBoardHardware * handle);

void FeedWatchdogTask(ControlBoardHardware * handle);

void UART_RX_ISR(ControlBoardHardware * handle);

void CAN_RX_ISR(CAN_HandleTypeDef *hcan);

#endif /* INC_CONTROLBOARD_H_ */
