/*
 * ControlBoard.c
 *
 *  Created on: Oct. 14, 2021
 *      Author: lvoze
 */

#include <ControlBoard.h>
#include "cmsis_os.h"

//For sprintf and memcpy
#include "string.h"

#include "stdio.h"

//For atoi
#include "stdlib.h"
//For ceil()
#include "math.h"

uint8_t can_rx_data[8];
CAN_RxHeaderTypeDef can_rx_header;

uint8_t can_tx_data[8] = {0, 0, 0, 0, 0, 0, 0, 0};
CAN_TxHeaderTypeDef can_tx_header = {0x200, 0, CAN_ID_STD, CAN_RTR_DATA, 8};

uint8_t uart_rec_buff[24];
uint8_t uart_tx_buff[128];

int8_t cmdcharbuffindex = 0;
uint8_t cmdbuff[20][24];
int8_t cmdbuffindex = 0;

uint8_t processingcommand = 0;
uint8_t cmdlen = 0;

//Create array of message structs to hold our filter information
struct message messageArray[16];

//Define starting filter array used on startup
const struct message defaultMessageArray[16] =
{
		//{ 0x370,   0,  16,   -1,  MSG_ENABLED  },  //Engine RPM
		{ 0x360,   0,  16,   -1,  MSG_ENABLED  },  //Engine RPM
		{ 0x360,  32,  16,   -1,  MSG_ENABLED  },  //Throttle Position

		{ 0x361,  16,  16,   -1,  MSG_ENABLED  },  //Oil Pressure

		{ 0x3E0,   0,  16,   -1,  MSG_ENABLED  },  //Coolant Temperature

		{ 0x390,   0,  16,   -1,  MSG_ENABLED  },  //Brake Pressure
		{ 0x390,   0,  16,   -1,  MSG_ENABLED  },  //Brake Bias
		{ 0x390,   0,  16,   -1,  MSG_ENABLED  },  //Lat Accel
		{ 0x390,   0,  16,   -1,  MSG_ENABLED  },  //Long Accel

		{ 0x370,   0,  16,   -1,  MSG_ENABLED  },  //GPS Speed

		{ 0x3E0,   48,  16,   -1,  MSG_ENABLED  },  //Oil Temperature

		{ 0x373,   0,  16,   -1,  MSG_ENABLED  },  //EGT 1

		{ 0x368,   0,  16,   -1,  MSG_ENABLED  },  //Wideband

		{ 0x3EB,  32,  16,   -1,  MSG_ENABLED  },  //Ignition Angle

		{     0,   0,   0,   -1,  MSG_DISABLED },  //Disabled
		{     0,   0,   0,   -1,  MSG_DISABLED },  //Disabled
		{     0,   0,   0,   -1,  MSG_DISABLED }   //Disabled
};

void InitControlboard(ControlBoardHardware * handle)
{
	//Setup UJA hardware references

	/*
	HAL_GPIO_WritePin(LD1_GPIO_Port, LD1_Pin, 0);
	HAL_GPIO_WritePin(LD2_GPIO_Port, LD2_Pin, 0);
	HAL_GPIO_WritePin(UJA_CS_GPIO_Port, UJA_CS_Pin, 1);
	*/

	UJA1075A_Init(&handle->SBC_Handle);

	//Load default message configuration
	//NOTE: This operation takes approximately 100ms!!!!!
	memcpy(&messageArray, &defaultMessageArray, sizeof(messageArray));

	//Initialize CAN and all filters
	Init_CAN(handle);

	//Start receiving UART
	HAL_UART_Receive_IT(handle->UART_Handle, uart_rec_buff, 1);

	//Send reset character "$" to notify telemetry software a reboot has occured and we need a new copy of filter configuration
	uint8_t uart_tx_buff[1] = {36};
	HAL_UART_Transmit_IT(handle->UART_Handle, uart_tx_buff, 1);
}

//Procedurally generates and sets CAN Filter configurations from the message[] struct array config
void ConfigureCANFilters(ControlBoardHardware * handle, struct message * messageArray, uint8_t size)
{
	uint32_t configuredIDs[size];
	int uniques = 0;
	for (int i = 0; i < size; i++)
	{
		struct message thismessage = messageArray[i];

		//Check if this ID already configured
		int create = 1;
		for (int j = 0; j < size; j++)
		{
			if (configuredIDs[j] == thismessage.id)
			{
				create = 0;
			}
		}
		if (create == 1 && thismessage.enabled)
		{
			//Add this ID to the list of already configured ID's to skip duplicates
			configuredIDs[uniques] = thismessage.id;
			CAN_FilterTypeDef filter;

			//This bit shifting was a massive PITA to figure out... see page 1092 of the RM for reasoning
			filter.FilterIdHigh = ((thismessage.id << 5)  | (thismessage.id >> (32 - 5))) & 0xFFFF;
			filter.FilterIdLow = (thismessage.id >> (11 - 3)) & 0xFFF8;

			//Masks set to full rank to check every bit against ID
			filter.FilterMaskIdHigh = 0xFFFF;
			filter.FilterMaskIdLow = 0xFFFF;

			//Filter options
			filter.FilterScale = CAN_FILTERSCALE_32BIT;
			filter.FilterActivation = ENABLE;
			filter.FilterMode = CAN_FILTERMODE_IDMASK;
			filter.FilterFIFOAssignment = CAN_FILTER_FIFO0;

			//Set filter bank to the current count of uniques
			filter.FilterBank = uniques;

			//Finally pass filter to HAL
			HAL_CAN_ConfigFilter(handle->CAN_Handle, &filter);
			uniques++;
		}
	}
}

void ClearCANBuffers(void)
{
	for (int i = 0; i < 16; i++) {
		messageArray[i].value = -1;
	}
}

void Init_CAN(ControlBoardHardware * handle)
{
	//Configure all receive filters from the config array
	ConfigureCANFilters(handle, messageArray, sizeof(messageArray) / sizeof(struct message));

	//Start CAN operation
	HAL_CAN_Start(handle->CAN_Handle);

	//Enable Message Pending IRQ
	HAL_CAN_ActivateNotification(handle->CAN_Handle, CAN_IT_RX_FIFO0_MSG_PENDING);

	//Start receiving - don't think we need this here
	HAL_CAN_GetRxMessage(handle->CAN_Handle, CAN_RX_FIFO0, &can_rx_header, can_rx_data);
}

void SendCANFramesTask(ControlBoardHardware * handle)
{
	osDelay(100);
	uint32_t mailbox;
	HAL_CAN_AddTxMessage(handle->CAN_Handle, &can_tx_header, can_tx_data, &mailbox);
}

void ProcessCommandTask(ControlBoardHardware * handle)
{
	//Wait for semaphore passed by UART IRQ when the command buffer is ready for processing
	osSemaphoreAcquire(handle->ProcessCommandSemaphore_Handle, osWaitForever);

	HAL_GPIO_TogglePin(handle->LED2_GPIO_Port, handle->LED2_GPIO_Pin);

	//Evaluate first char of the command buffer to determine command
	if (cmdbuff[cmdbuffindex-1][0] == CMD_RETURN_CHAR) //Restart
	{
		//Force a system reset
		NVIC_SystemReset();
	}
	else if (cmdbuff[cmdbuffindex-1][0] == CMD_SET_FILTER) //Set filter
	{
		//Series of atoi to split up command string
		int filter = atoi((char *)&cmdbuff[cmdbuffindex-1][1]);
		uint16_t id = atoi((char *)&cmdbuff[cmdbuffindex-1][3]);
		uint8_t bit = atoi((char *)&cmdbuff[cmdbuffindex-1][8]);
		uint8_t size = atoi((char *)&cmdbuff[cmdbuffindex-1][11]);

		//Put received data into array
		messageArray[filter].id = id;
		messageArray[filter].bit = bit;
		messageArray[filter].value = -1;
		messageArray[filter].length = size;
		messageArray[filter].enabled = (id != 0)? MSG_ENABLED : MSG_DISABLED;

	}
	else if (cmdbuff[cmdbuffindex-1][0] == CMD_RESTART) //Shutdown
	{
		//Sets can_tx frame shutdown bit to 1
		can_tx_data[0] |= CAN_TXFRAME0_SHUTDOWN;
	}

	//Finally decrement command buffer index as we have processed this command.
	cmdbuffindex--;

	//If we reach the last command in buffer, re-configure all CAN filters with new data.
	if (cmdbuffindex == 0)
	{
		ConfigureCANFilters(handle, messageArray, 16);
	}
}

void SendTelemetryTask(ControlBoardHardware * handle)
{
	osDelay(100);

	//TODO Switch to static allocation
	sprintf((char *)&uart_tx_buff, "%i,%i,%i,%i,%i,%i,%i,%i,%i,%i,%i,%i,%i,%i,%i,%i\r\n",
					(int)messageArray[0].value,
					(int)messageArray[1].value,
					(int)messageArray[2].value,
					(int)messageArray[3].value,
					(int)messageArray[4].value,
					(int)messageArray[5].value,
					(int)messageArray[6].value,
					(int)messageArray[7].value,
					(int)messageArray[8].value,
					(int)messageArray[9].value,
					(int)messageArray[10].value,
					(int)messageArray[11].value,
					(int)messageArray[12].value,
					(int)messageArray[13].value,
					(int)messageArray[14].value,
					(int)messageArray[15].value);

	//Transmit our message
	HAL_UART_Transmit_IT(handle->UART_Handle, uart_tx_buff, strlen((char *)uart_tx_buff));

	//Clear all the received values to -1 in order to detect when we aren't receiving updates.
	ClearCANBuffers();
}

void FeedWatchdogTask(ControlBoardHardware * handle)
{
	//600 milliseconds is in the lower end of the watchdog window as currently configured in the SBC.
	osDelay(600);

	UJA1075A_FeedWD(&handle->SBC_Handle);

	//Toggle LED
	HAL_GPIO_TogglePin(handle->LED1_GPIO_Port,handle->LED1_GPIO_Pin);
}

void UART_RX_ISR(ControlBoardHardware * handle)
{
	//Check if enter or cmdbuff reaches its limit (prevents overflow)
	if (uart_rec_buff[0] == CMD_RETURN_CHAR || cmdcharbuffindex > 23)
	{
		//Make sure theres more than just \r sent.
		if (cmdcharbuffindex != 0)
		{
			//Increase command buffer index
			cmdbuffindex++;

			//Limit number of commands to 16.
			if (cmdbuffindex > 16)
			{
				cmdbuffindex = 16;
			}
			//Pass command onto task
			osSemaphoreRelease(handle->ProcessCommandSemaphore_Handle);

			//Reset char index
			cmdcharbuffindex = 0;
		}
	}
	else
	{
		//Put received char into buffer
		cmdbuff[cmdbuffindex][cmdcharbuffindex] = uart_rec_buff[0];
		//Increase char index
		cmdcharbuffindex++;
	}

	//Start receiving again
	HAL_UART_Receive_IT(handle->UART_Handle, uart_rec_buff, 1);
}

void CAN_RX_ISR(CAN_HandleTypeDef *hcan)
{
	//Get the received message.
	HAL_CAN_GetRxMessage(hcan, CAN_RX_FIFO0, &can_rx_header, can_rx_data);

	//Parse received bytes using message array
	for(int i=0; i < sizeof(messageArray) / sizeof(struct message); i++)
	{
		if(messageArray[i].id == can_rx_header.StdId)
		{

			//Calculate which byte position to start at
			int bytepos = messageArray[i].bit / 8;

			//Calculate number of bytes that need to be checked
			int bytes = ceil(messageArray[i].length / (float)8);

			uint32_t finalval = 0;
			int j = 0;

			//Iterate through all bytes that must be read for this message
			for (int b = bytepos; b < bytepos + bytes; b++)
			{
				uint8_t tempval;
				//If on last byte we may need to truncate unneeded parts dependent on length of data
				if (b == bytepos + bytes - 1)
				{
					//We need a left shift and a right shift to extract the bits we want
					uint8_t byteoffset = (messageArray[i].length - ((bytes-1) * 8));
					uint8_t leftshift = 8 - (messageArray[i].bit - (bytepos * 8)) - byteoffset;
					uint8_t rightshift = 8 - byteoffset;
					tempval = (can_rx_data[b] << leftshift) >>  rightshift;
				}
				else
				{
					//Use the whole byte
					tempval = can_rx_data[b];
				}
				//Calculate the size of the next data section to find the required shift
				int nextsize = messageArray[i].length - ((j+1) * 8);

				//Limit it to 0
				if (nextsize < 0)
				{
					nextsize = 0;
				}
				finalval += tempval << nextsize;
				j++;
			}

			//Finally set final value into message array struct
			messageArray[i].value = finalval;
		}
	}
}
