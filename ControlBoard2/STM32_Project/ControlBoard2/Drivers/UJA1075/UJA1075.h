/*
 * UJA1075.h
 *
 *  Created on: Oct. 14, 2021
 *      Author: lvoze
 */

#ifndef INC_UJA1075_H_
#define INC_UJA1075_H_

#include "stm32f3xx_hal.h"

typedef struct
{
	SPI_HandleTypeDef * SPI_Handle;
	GPIO_TypeDef * ChipSelect_GPIO_Port;
	uint32_t ChipSelect_GPIO_Pin;
} UJA1075_Handle;

//UJA Register Definitions
#define UJA_REG_WDGANDSTATUS 0
#define UJA_REG_MODECONTROL 1
#define UJA_REG_INTCON 2
#define UJA_REG_INTREAD 3

//WD_and_Status register
//RO
#define UJA_RO_RW 0
#define UJA_RO_R 1

//WMC
#define UJA_WMC_WND 0
#define UJA_WMC_TO 1

//NWP
#define UJA_NWP_8 0
#define UJA_NWP_16 1
#define UJA_NWP_32 2
#define UJA_NWP_64 3
#define UJA_NWP_128 4
#define UJA_NWP_256 5
#define UJA_NWP_1024 6
#define UJA_NWP_4096 7


//Mode_Control register
#define UJA_MC_STBY 0
#define UJA_MC_SLP 1
#define UJA_MC_V2OFF 2
#define UJA_MC_V2ON 3

//Int_Control register
#define UJA_V1UIE_OFF 0
#define UJA_V1UIE_ON 1

#define UJA_V2UIE_OFF 0
#define UJA_V2UIE_ON 1

//This defines the WD configuration set on both startup and when feeding watchdog
const uint8_t WD_SETUP = (UJA_REG_WDGANDSTATUS << 5) | (UJA_RO_RW << 4) | (UJA_WMC_WND << 3) | (UJA_NWP_1024);

/**
 * @brief Initializes UJA
 *
 * @param handle
 */
void UJA1075A_Init(UJA1075_Handle * handle);

/**
 * @brief Feed the UJA's watchdog
 *
 * @param handle
 */
void UJA1075A_FeedWD(UJA1075_Handle * handle);

/**
 * @brief Writes the provided txdata to the UJA over SPI
 *
 * @param handle
 * @param txdata
 */
void UJA1075A_Write(UJA1075_Handle * handle, uint8_t * txdata);

#endif /* INC_UJA1075_H_ */
