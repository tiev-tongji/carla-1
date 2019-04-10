// Copyright (c) 2017 Computer Vision Center (CVC) at the Universitat Autonoma de Barcelona (UAB). This work is licensed under the terms of the MIT license. For a copy, see <https://opensource.org/licenses/MIT>.

#pragma once

#include "CarSimPawn.h"

#include "Vehicle/CarlaWheeledVehicleState.h"
#include "Vehicle/VehicleControl.h"
#include "Vehicle/VehicleInputPriority.h"
#include "Vehicle/VehiclePhysicsControl.h"
//#include "WheeledVehicleMovementComponent4W.h"

#include "CoreMinimal.h"
#include "CarlaCarSimVehicle.generated.h"

class UBoxComponent;
class UCarSimAgentComponent;

UCLASS()
class CARLA_API ACarlaCarSimVehicle : public ACarsimPawn
{
	GENERATED_BODY()

public:
	// Sets default values for this pawn's properties
	ACarlaCarSimVehicle();

private:
	UPROPERTY(Category = "AI Controller", VisibleAnywhere)
		ECarlaWheeledVehicleState State = ECarlaWheeledVehicleState::UNKNOWN;

	UPROPERTY(Category = "CARLA CarSim Vehicle", EditAnywhere)
		UBoxComponent *VehicleBounds;

	UPROPERTY(Category = "CARLA CarSim Vehicle", VisibleAnywhere)
		UCarSimAgentComponent *CarSimAgentComponent;

	struct
	{
		EVehicleInputPriority Priority = EVehicleInputPriority::INVALID;
		FVehicleControl Control;
	}
	InputControl;

	FVehicleControl LastAppliedControl;
};
