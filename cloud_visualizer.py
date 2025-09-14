#!/usr/bin/env python3
from __future__ import print_function
import struct
import sys
import argparse
import math

PythonGateways = 'pythonGateways/'
sys.path.append(PythonGateways)

import VsiCommonPythonApi as vsiCommonPythonApi
import VsiTcpUdpPythonGateway as vsiEthernetPythonGateway


class MySignals:
	def __init__(self):
		# Inputs
		self.x = 0
		self.y = 0
		self.theta = 0



srcMacAddress = [0x12, 0x34, 0x56, 0x78, 0x9A, 0xBE]
sim_envMacAddress = [0x12, 0x34, 0x56, 0x78, 0x9A, 0xBD]
srcIpAddress = [192, 168, 1, 3]
sim_envIpAddress = [192, 168, 1, 2]

Sim_envSocketPortNumber0 = 8071

Visualizer0 = 0


# Start of user custom code region. Please apply edits only within these regions:  Global Variables & Definitions
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

class VisualizerPlot:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.ax.set_xlim(-5, 300)  # Adjust based on your expected path
        self.ax.set_ylim(-1, 4)
        self.ax.set_title('Line Following Robot Simulation (VSI)')
        self.ax.set_xlabel('X position (m)')
        self.ax.set_ylabel('Y position (m)')
        self.ax.grid(True)
        
        # Draw the reference path (simple horizontal line at y=0)
        self.ax.axhline(y=2, color='r', linestyle='--', label='Reference Path (y=0)')
        
        # Initialize robot trajectory and current position
        self.trajectory_line, = self.ax.plot([], [], 'b-', label='Robot Path')
        self.current_pos, = self.ax.plot([], [], 'go', markersize=8, label='Current Position')
        self.ax.legend()
        
        # Data containers
        self.x_data = []
        self.y_data = []

		# track KPIs
        # KPI tracking - FIXED VERSION
        self.errors = []  # Track lateral errors over time
        self.times = []   # Track simulation times in seconds
        self.max_error = 0
        self.settling_time = None
        self.steady_state_error = None
        self.overshoot = 0
        self.settling_detected = False
        
        # Reference value
        self.reference_y = 2
        self.settling_threshold = 0.05  # 5% threshold for settling
        
    def update_plot(self, x, y,time_ns):
		# Convert time to seconds
        time_s = time_ns / 1e9
        
        # Calculate current error
        current_error = abs(y - self.reference_y)
        
        # Store data for KPI calculation
        self.errors.append(current_error)
        self.times.append(time_s)
        if current_error > self.max_error:
            self.max_error = current_error
		############
        self.x_data.append(x)
        self.y_data.append(y)
        self.trajectory_line.set_data(self.x_data, self.y_data)
        self.current_pos.set_data([x], [y])
		##########
		# Calculate KPIs if we have enough data
        if len(self.errors) > 10:
            self.calculate_kpis()
		

        return self.trajectory_line, self.current_pos
    
    def calculate_kpis(self):
	# Calculate steady-state error (average of last 20% of data points)
        # Only calculate once we have sufficient data
        if len(self.errors) < 10:
            return
    
    # Calculate current steady-state error (moving average of recent errors)
        window_size = min(20, len(self.errors) // 4)  # Use 20 samples or 25% of data
        recent_errors = self.errors[-window_size:]
        current_ss_error = np.mean(recent_errors)
    
    # Update steady-state error if we have a reasonable value
        if current_ss_error > 1e-6:  # Ignore extremely small values
            self.steady_state_error = current_ss_error
    
    # Calculate overshoot in centimeters (not percentage!)
        if self.max_error > 0 and self.steady_state_error is not None:
        # Convert to centimeters: meters * 100

            self.overshoot = (self.max_error - self.steady_state_error) * 100  # cm
    
    # Detect settling time (only once)
        if not self.settling_detected and self.steady_state_error is not None:
            threshold = self.steady_state_error * (1 + self.settling_threshold)
        
        # Check if we've been within threshold for a while
            if len(self.errors) >= 30:  # Need enough data to check
                recent_errors = self.errors[-30:]
                if all(error <= threshold for error in recent_errors[-10:]):  # Last 10 samples
                # Find when settling first occurred
                    for i, error in enumerate(self.errors):
                        if error <= threshold:
                        # Check if it stayed within threshold
                            if all(e <= threshold for e in self.errors[i:i+10]):
                                self.settling_time = self.times[i]
                                self.settling_detected = True
                                break



    def print_kpis(self):
        if len(self.times) % 50 != 0:  # Print every 50 samples
            return
		
        print("\n======================== Key Performance Indicators ========================")
        print(f"Maximum Overshoot: {self.overshoot:.2f} cm")
		
        if self.settling_time is not None:
            print(f"Settling Time (5%): {self.settling_time:.2f}s")
        else:
            print(f"Settling Time (5%): Not yet settled")
		
        if self.steady_state_error is not None:
            print(f"Steady-State Error: {self.steady_state_error * 100:.4f} cm")  # Convert to cm
        else:
            print(f"Steady-State Error: Calculating...")
		
        print(f"Current Error: {self.errors[-1] * 100:.4f} cm")  # Current error in cm
        print("================================")


    def show(self):
        plt.show()


viz = VisualizerPlot()
plt.ion()  # Turn on interactive mode
# End of user custom code region. Please don't edit beyond this point.
class Visualizer:

	def __init__(self, args):
		self.componentId = 2
		self.localHost = args.server_url
		self.domain = args.domain
		self.portNum = 50103
        
		self.simulationStep = 0
		self.stopRequested = False
		self.totalSimulationTime = 0
        
		self.receivedNumberOfBytes = 0
		self.receivedPayload = []

		self.numberOfPorts = 1
		self.clientPortNum = [0] * self.numberOfPorts
		self.receivedDestPortNumber = 0
		self.receivedSrcPortNumber = 0
		self.expectedNumberOfBytes = 0
		self.mySignals = MySignals()

		# Start of user custom code region. Please apply edits only within these regions:  Constructor

		# End of user custom code region. Please don't edit beyond this point.



	def mainThread(self):
		dSession = vsiCommonPythonApi.connectToServer(self.localHost, self.domain, self.portNum, self.componentId)
		vsiEthernetPythonGateway.initialize(dSession, self.componentId, bytes(srcMacAddress), bytes(srcIpAddress))
		try:
			vsiCommonPythonApi.waitForReset()

			# Start of user custom code region. Please apply edits only within these regions:  After Reset

			# End of user custom code region. Please don't edit beyond this point.
			self.updateInternalVariables()

			if(vsiCommonPythonApi.isStopRequested()):
				raise Exception("stopRequested")
			self.establishTcpUdpConnection()
			nextExpectedTime = vsiCommonPythonApi.getSimulationTimeInNs()
			while(vsiCommonPythonApi.getSimulationTimeInNs() < self.totalSimulationTime):

				# Start of user custom code region. Please apply edits only within these regions:  Inside the while loop

				# End of user custom code region. Please don't edit beyond this point.

				self.updateInternalVariables()

				if(vsiCommonPythonApi.isStopRequested()):
					raise Exception("stopRequested")

				if(vsiEthernetPythonGateway.isTerminationOnGoing()):
					print("Termination is on going")
					break

				if(vsiEthernetPythonGateway.isTerminated()):
					print("Application terminated")
					break

				receivedData = vsiEthernetPythonGateway.recvEthernetPacket(Sim_envSocketPortNumber0)
				if(receivedData[3] != 0):
					self.decapsulateReceivedData(receivedData)

				# Start of user custom code region. Please apply edits only within these regions:  Before sending the packet
				# In your main loop, replace the printing call:
				try:
					current_time = vsiCommonPythonApi.getSimulationTimeInNs()
					viz.update_plot(self.mySignals.x, self.mySignals.y, current_time)
					
					# Print KPIs less frequently to avoid spam
					if int(current_time / 1e9) % 2 == 0:  # Print every 2 seconds
						viz.print_kpis()
						
					plt.pause(0.01)
				except Exception as e:
					print(f"Plotting error: {e}")
				# End of user custom code region. Please don't edit beyond this point.

				# Start of user custom code region. Please apply edits only within these regions:  After sending the packet

				# End of user custom code region. Please don't edit beyond this point.

				print("\n+=visualizer+=")
				print("  VSI time:", end = " ")
				print(vsiCommonPythonApi.getSimulationTimeInNs(), end = " ")
				print("ns")
				print("  Inputs:")
				print("\tx =", end = " ")
				print(self.mySignals.x)
				print("\ty =", end = " ")
				print(self.mySignals.y)
				print("\ttheta =", end = " ")
				print(self.mySignals.theta)
				print("\n\n")

				self.updateInternalVariables()

				if(vsiCommonPythonApi.isStopRequested()):
					raise Exception("stopRequested")
				nextExpectedTime += self.simulationStep

				if(vsiCommonPythonApi.getSimulationTimeInNs() >= nextExpectedTime):
					continue

				if(nextExpectedTime > self.totalSimulationTime):
					remainingTime = self.totalSimulationTime - vsiCommonPythonApi.getSimulationTimeInNs()
					vsiCommonPythonApi.advanceSimulation(remainingTime)
					break

				vsiCommonPythonApi.advanceSimulation(nextExpectedTime - vsiCommonPythonApi.getSimulationTimeInNs())

			if(vsiCommonPythonApi.getSimulationTimeInNs() < self.totalSimulationTime):
				vsiEthernetPythonGateway.terminate()
		except Exception as e:
			if str(e) == "stopRequested":
				print("Terminate signal has been received from one of the VSI clients")
				# Advance time with a step that is equal to "simulationStep + 1" so that all other clients
				# receive the terminate packet before terminating this client
				vsiCommonPythonApi.advanceSimulation(self.simulationStep + 1)
			else:
				print(f"An error occurred: {str(e)}")
		except:
			# Advance time with a step that is equal to "simulationStep + 1" so that all other clients
			# receive the terminate packet before terminating this client
			vsiCommonPythonApi.advanceSimulation(self.simulationStep + 1)
		print("\n" + "="*60)
		print("FINAL PERFORMANCE RESULTS")
		print("="*60)
		viz.print_kpis()



	def establishTcpUdpConnection(self):
		if(self.clientPortNum[Visualizer0] == 0):
			self.clientPortNum[Visualizer0] = vsiEthernetPythonGateway.tcpConnect(bytes(sim_envIpAddress), Sim_envSocketPortNumber0)

		if(self.clientPortNum[Visualizer0] == 0):
			print("Error: Failed to connect to port: Sim_env on TCP port: ") 
			print(Sim_envSocketPortNumber0)
			exit()



	def decapsulateReceivedData(self, receivedData):
		self.receivedDestPortNumber = receivedData[0]
		self.receivedSrcPortNumber = receivedData[1]
		self.receivedNumberOfBytes = receivedData[3]
		self.receivedPayload = [0] * (self.receivedNumberOfBytes)

		for i in range(self.receivedNumberOfBytes):
			self.receivedPayload[i] = receivedData[2][i]

		if(self.receivedSrcPortNumber == Sim_envSocketPortNumber0):
			print("Received packet from sim_env")
			receivedPayload = bytes(self.receivedPayload)
			self.mySignals.x, receivedPayload = self.unpackBytes('d', receivedPayload)

			self.mySignals.y, receivedPayload = self.unpackBytes('d', receivedPayload)

			self.mySignals.theta, receivedPayload = self.unpackBytes('d', receivedPayload)


		# Start of user custom code region. Please apply edits only within these regions:  Protocol's callback function

		# End of user custom code region. Please don't edit beyond this point.



	def packBytes(self, signalType, signal):
		if isinstance(signal, list):
			if signalType == 's':
				packedData = b''
				for str in signal:
					str += '\0'
					str = str.encode('utf-8')
					packedData += struct.pack(f'={len(str)}s', str)
				return packedData
			else:
				return struct.pack(f'={len(signal)}{signalType}', *signal)
		else:
			if signalType == 's':
				signal += '\0'
				signal = signal.encode('utf-8')
				return struct.pack(f'={len(signal)}s', signal)
			else:
				return struct.pack(f'={signalType}', signal)



	def unpackBytes(self, signalType, packedBytes, signal = ""):
		if isinstance(signal, list):
			if signalType == 's':
				unpackedStrings = [''] * len(signal)
				for i in range(len(signal)):
					nullCharacterIndex = packedBytes.find(b'\0')
					if nullCharacterIndex == -1:
						break
					unpackedString = struct.unpack(f'={nullCharacterIndex}s', packedBytes[:nullCharacterIndex])[0].decode('utf-8')
					unpackedStrings[i] = unpackedString
					packedBytes = packedBytes[nullCharacterIndex + 1:]
				return unpackedStrings, packedBytes
			else:
				unpackedVariable = struct.unpack(f'={len(signal)}{signalType}', packedBytes[:len(signal)*struct.calcsize(f'={signalType}')])
				packedBytes = packedBytes[len(unpackedVariable)*struct.calcsize(f'={signalType}'):]
				return list(unpackedVariable), packedBytes
		elif signalType == 's':
			nullCharacterIndex = packedBytes.find(b'\0')
			unpackedVariable = struct.unpack(f'={nullCharacterIndex}s', packedBytes[:nullCharacterIndex])[0].decode('utf-8')
			packedBytes = packedBytes[nullCharacterIndex + 1:]
			return unpackedVariable, packedBytes
		else:
			numBytes = 0
			if signalType in ['?', 'b', 'B']:
				numBytes = 1
			elif signalType in ['h', 'H']:
				numBytes = 2
			elif signalType in ['f', 'i', 'I', 'L', 'l']:
				numBytes = 4
			elif signalType in ['q', 'Q', 'd']:
				numBytes = 8
			else:
				raise Exception('received an invalid signal type in unpackBytes()')
			unpackedVariable = struct.unpack(f'={signalType}', packedBytes[0:numBytes])[0]
			packedBytes = packedBytes[numBytes:]
			return unpackedVariable, packedBytes

	def updateInternalVariables(self):
		self.totalSimulationTime = vsiCommonPythonApi.getTotalSimulationTime()
		self.stopRequested = vsiCommonPythonApi.isStopRequested()
		self.simulationStep = vsiCommonPythonApi.getSimulationStep()



def main():
	inputArgs = argparse.ArgumentParser(" ")
	inputArgs.add_argument('--domain', metavar='D', default='AF_UNIX', help='Socket domain for connection with the VSI TLM fabric server')
	inputArgs.add_argument('--server-url', metavar='CO', default='localhost', help='server URL of the VSI TLM Fabric Server')

	# Start of user custom code region. Please apply edits only within these regions:  Main method

	# End of user custom code region. Please don't edit beyond this point.

	args = inputArgs.parse_args()
                      
	visualizer = Visualizer(args)
	visualizer.mainThread()



if __name__ == '__main__':
    main()
