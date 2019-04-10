// Copyright (c) 2017 Computer Vision Center (CVC) at the Universitat Autonoma de Barcelona (UAB). This work is licensed under the terms of the MIT license. For a copy, see <https://opensource.org/licenses/MIT>.

//#include "Carla.h"
//#include "TireConfig.h"
#include "CarlaCarSimVehicle.h"
//#include "VehicleWheel.h"

#include "Agent/CarSimAgentComponent.h"

#include "Components/BoxComponent.h"
#include "Engine/CollisionProfile.h"

ACarlaCarSimVehicle::ACarlaCarSimVehicle()
	: Super()
{
	VehicleBounds = CreateDefaultSubobject<UBoxComponent>(TEXT("VehicleBounds"));
	VehicleBounds->SetupAttachment(RootComponent);
	VehicleBounds->SetHiddenInGame(true);
	VehicleBounds->SetCollisionProfileName(UCollisionProfile::NoCollision_ProfileName);

	CarSimAgentComponent = CreateDefaultSubobject<UCarSimAgentComponent>(TEXT("CarSimAgentComponent"));
	CarSimAgentComponent->SetupAttachment(RootComponent);

	//CarSim插件中无此变量
	//GetVehicleMovementComponent()->bReverseAsBrake = false;
}
