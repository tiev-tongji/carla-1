// Copyright (c) 2017 Computer Vision Center (CVC) at the Universitat Autonoma de Barcelona (UAB). This work is licensed under the terms of the MIT license. For a copy, see <https://opensource.org/licenses/MIT>.

#include "Carla.h"
#include "CarSimAgentComponent.h"

//为什么在VehicleAgentComponent中不需要添加声明也正确编译？
#include "Vehicle/CarSimVehicleAIController.h"
static bool IsPlayer(const ACarlaCarSimVehicle &InVehicle)
{
	auto *Controller = Cast<ACarSimVehicleAIController>(InVehicle.GetController());
	return (Controller != nullptr) && Controller->IsPossessingThePlayer();
}

UCarSimAgentComponent::UCarSimAgentComponent(const FObjectInitializer &ObjectInitializer)
	: Super(ObjectInitializer) {}

void UCarSimAgentComponent::BeginPlay()
{
	Vehicle = Cast<ACarlaCarSimVehicle>(GetOwner());
	checkf(Vehicle != nullptr, TEXT("UCarSimAgentComponent can only be attached to ACarlaCarSimVehicle"));

	// We only want to register non-player agents.
	bRegisterAgentComponent = !IsPlayer(*Vehicle);

	Super::BeginPlay();
}
