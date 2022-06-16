/*
 * SLAB8051.h
 *
 *  Created on: Dec 3, 2012
 *      Author: barmstro
 */

#ifndef SLAB8051_H_
#define SLAB8051_H_

/////////////////////////////////////////////////////////////////////////////
// DLL Preprocessor Definitions
/////////////////////////////////////////////////////////////////////////////

#ifdef __WIN32__
 #ifdef SLAB_8051_UTIL_EXPORTS
  #define SLAB_8051_UTIL_API __declspec(dllexport)
 #else
  #define SLAB_8051_UTIL_API __declspec(dllimport)
 #endif
#elif __linux__
 #define SLAB_8051_UTIL_API __attribute__ ((visibility ("default")))
#elif __MACH__
 #define SLAB_8051_UTIL_API
#else
 #error "Detected OS not supported"
#endif


/////////////////////////////////////////////////////////////////////////////
// Cross platform definitions
/////////////////////////////////////////////////////////////////////////////

#include "stdafx.h"

/////////////////////////////////////////////////////////////////////////////
// Definitions
/////////////////////////////////////////////////////////////////////////////
#ifndef CALLBACK
#define CALLBACK            __stdcall
#endif
#ifndef WINAPI
#define WINAPI              __stdcall
#endif

/////////////////////////////////////////////////////////////////////////////
// String Definitions
/////////////////////////////////////////////////////////////////////////////

// An ASCII, null-terminated device string used when retrieving a
// serial string or device path string
typedef char SLAB8051_DEVICE_STR[MAX_PATH];

/////////////////////////////////////////////////////////////////////////////
// Macro Definitions
/////////////////////////////////////////////////////////////////////////////

#include "SLAB8051Errors.h"
#define SLAB8051_SUCCEEDED(status) ((status) == SLAB8051_DEVICE_SUCCESS)
#define SLAB8051_FAILED(status) ((status) != SLAB8051_DEVICE_SUCCESS)

/////////////////////////////////////////////////////////////////////////////
// Type Definitions
/////////////////////////////////////////////////////////////////////////////

// Return Code -- see SLAB8051Errors.h
typedef int SLAB8051_STATUS;

// A SLAB_8051_DEVICE device object pointer used to access 8051 Debug Adapters
typedef void* SLAB8051_DEVICE;

// A progress callback used to indicate progress of time-lengthy operations
//
// percent indicates the progress in percent between 0 and 100.
// workInProgress - TRUE to continue operation in progress, FALSE to abort the operation
//

/////////////////////////////////////////////////////////////////////////////
// Exported Library Functions
/////////////////////////////////////////////////////////////////////////////

#ifdef __cplusplus
extern "C" {
#endif // __cplusplus
typedef BOOL (CALLBACK *SLAB8051_PROGRESS_CALLBACK)(int percent, /*BOOL workInProgress,*/ void* userData);

SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI GetSLAB8051Version(BYTE* major, BYTE* minor, BOOL* release);

// Enumeration & connection
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI USBDebugDevices(DWORD *dwDevices);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI GetUSBDeviceSN(DWORD dwDeviceNum, const char ** psSerialNum);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI GetDeviceName(const char **psDeviceName);
SLAB_8051_UTIL_API BOOL WINAPI IsUSBConnected(const char* sSerialNum);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI ConnectUSB(const char* sSerialNum, int nECprotocol=0, int nPowerTarget=0, bool resetAndHalt=true);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI DisconnectUSB(bool reset=true);

// Identification
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI GetDerivativeID(BYTE *pbDerivativeID);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI GetDerivativeRev(BYTE *pbDerivativeRev);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI GetHardwareID(unsigned short *pUsHardwareID);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI GetHardwareRev(BYTE *pbHardwareRev);

// Target Control
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI GetTargetStatus(int *ptrStatus);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI TargetReset();

// Debug Support
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI SetClrBP(int nSet, DWORD wBPAddress);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI SetTargetGo();
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI SetTargetHalt();
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI TargetStep();

// Memory I/F
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI GetCodeMemory(BYTE* ptrMem, DWORD wStartAddress, unsigned int nLength);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI GetRAMMemory(BYTE* ptrMem, DWORD wStartAddress, unsigned int nLength);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI GetSFRMemory(BYTE * ptrMem, DWORD wStartAddress, unsigned int nLength);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI GetXRAMMemory(BYTE * ptrMem, DWORD wStartAddress, unsigned int nLength);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI GetScratchPadMemory(BYTE * ptrMem, DWORD wStartAddress, unsigned int	nLength);

SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI SetCodeMemory(BYTE * ptrMem, DWORD wStartAddress, unsigned int nLength);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI SetRAMMemory(BYTE * ptrMem, DWORD wStartAddress, unsigned int nLength);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI SetSFRMemory(BYTE * ptrMem, DWORD wStartAddress, unsigned int nLength);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI SetXRAMMemory(BYTE *	ptrMem, DWORD wStartAddress, unsigned int nLength);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI SetScratchPadMemory(BYTE * ptrMem, DWORD wStartAddress, unsigned int	nLength);

// Flash Programming
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI Download(char *sDownloadFile, SLAB8051_PROGRESS_CALLBACK progress, void* userData,
		int nDeviceErase = 0, int nDownloadScratchPadSFLE = 0, int nBankSelect = -1, int nLockFlash = 0,
		BOOL bPersistFlash = TRUE, BOOL bVerifyFlash = FALSE);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI UserSpaceErase();
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI LockFlash();
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI FlashLocked(bool &locked);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI ISupportBanking(int * nSupportedBanks);

// Register I/F
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI ReadPC(DWORD *ptrPC);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI WritePC(DWORD wPC);

// DSR Support
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI SetDSRPresent(BYTE nDSR);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI SetDSRDerivativeValue(BYTE nDSRDeriv);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI NoDSR_SetSFRregister(BYTE bSFRAddress, BYTE bValue);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI NoDSR_GetSFRregister(BYTE bSFRAddress, BYTE* bValue);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI SendByteCommand(BYTE bCommand);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI DownloadDSR(const char* sAdapterSN, char *sDSRFile, WORD nHWID, BYTE bDSRID, int nECprotocol=0);

// Streaming Support
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI StartStreaming(unsigned int scanRate);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI StopStreaming();
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI ReadStream(unsigned int nLength, BYTE * ptrMem);

// MISC
SLAB_8051_UTIL_API char* WINAPI GetErrorMsg (SLAB8051_STATUS errorCode);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI GetCurrentActiveBank(BYTE& bank);

// DSR Testing Support
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI SetSFRByte(DWORD SFRAddress, BYTE SFRVal);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI GetSFRByte(DWORD SFRAddress, BYTE *pSFRVal);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI IndSetSFRByte(DWORD SFRAddress, BYTE SFRVal);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI IndGetSFRByte(DWORD SFRAddress, BYTE *pSFRVal);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI GetPageCRC(BYTE dPage, BYTE *pCRC);
SLAB_8051_UTIL_API SLAB8051_STATUS WINAPI C2MakeOTP();

#ifdef __cplusplus
}
#endif // __cplusplus


#endif /* SLAB_8051_UTIL_H_ */
