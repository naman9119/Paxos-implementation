from collections import Counter

class Proposer:
    def __init__(self, acceptors, distinguished=False):
        self.acceptors = acceptors
        self.distinguished = distinguished
        self.number = 1  # Initialize the proposal number
        self.values = ['A', 'B', 'C', 'D']  # Initialize the list of proposal values
        self.preparing_acceptors = []  # List to store acceptors responding to prepare requests

    def send_prepare_requests(self):
        print('Start sending prepare requests for proposer', self.number)

        self.preparing_acceptors = []  # Reset the list of preparing acceptors
        highest_res_num = -1  # Variable to track the highest response number received

        for acceptor in self.acceptors:  # Iterate over each acceptor
            print('  Send a prepare request to ' + str(acceptor) +
                  ' with no = ' + str(self.number) + '.')

            try:
                response = acceptor.prepare(self.number)  # Send prepare request to acceptor
            except IOError:
                print('  Failed to send a prepare request to ' + str(acceptor) + '.')
                continue

            self.preparing_acceptors.append(acceptor)  # Add acceptor to preparing acceptors list

            if response is not None:  # Check if response is received
                res_number, res_value = response  # Unpack response
                if res_number > highest_res_num:
                    highest_res_num = res_number
                    self.value = res_value

        num_acceptors = len(self.acceptors)
        num_preparing = len(self.preparing_acceptors)

        print(str(num_preparing) + ' / ' + str(num_acceptors) + ' are preparing.')

        if num_preparing < num_acceptors // 2 + 1:  # Check if preparing acceptors form a majority
            print('Acceptors that responded to a prepare request are not majority.')
            return

        print('Finish sending prepare requests for proposer', self.number)

    def send_accept_requests(self):
        print('Start to send accept requests for proposer', self.number)

        for acceptor in self.preparing_acceptors:  # Iterate over preparing acceptors
            print('  Send an accept request to ' + str(acceptor) +
                  ' with no = ' + str(self.number) +
                  ', value = "' + str(self.values[self.number - 1]) + '".')
            try:
                acceptor.accept(self.number, self.values[self.number - 1])  # Send accept request to acceptor
            except IOError:
                print('  Failed to send an accept request to ' + str(acceptor))

        print('Finish sending accept requests for proposer', self.number)

        self.number += 1  # Increment proposal number after sending accept requests



class Acceptor:

    def __init__(self, name, learners):
        self.name = name  # Acceptor name
        self.learners = learners  # List of learners
        self.prepared_number = 1  # Initialize the prepared proposal number
        self.accepted_number = 2  # Initialize the accepted proposal number
        self.accepted_value = None  # Initialize the accepted proposal value

    def __str__(self):
        return self.name

    def prepare(self, proposal_number):
        if proposal_number <= self.prepared_number:  # Check if proposal number is less than or equal to prepared number
            return None

        self.prepared_number = proposal_number  # Update prepared number
        return self.accepted_number, self.accepted_value  # Return accepted number and value

    def accept(self, proposal_number, proposal_value):
        if proposal_number < self.prepared_number:  # Check if proposal number is less than prepared number
            return

        self.accepted_number = proposal_number  # Update accepted number
        self.accepted_value = proposal_value  # Update accepted value

        for learner in self.learners:  # Inform learners about accepted value
            learner.learn_accepted_value(
                self.name, proposal_number, proposal_value)

class Learner:
    def __init__(self, num_acceptors):
        self.num_acceptors = num_acceptors
        self.accepting_acceptors = []
        self.accepted_value = None
        self.accepted_proposal_number = -1  # Initialize with a number lower than any proposal number

    def learn_accepted_value(self, name, proposal_number, proposal_value):
        print('  ' + str(name) + ' accepted "' +
              str(proposal_value) + '".')

        self.accepting_acceptors.append(name)

        # Check if the received proposal number is higher than the previously accepted one
        if proposal_number > self.accepted_proposal_number:
            self.accepted_value = proposal_value
            self.accepted_proposal_number = proposal_number

    def get_chosen_value(self):
        if not self.accepting_acceptors:
            print('No value has been accepted yet.')
            return None

        if len(self.accepting_acceptors) < self.num_acceptors // 2 + 1:
            print('The accepted value is not chosen by a majority of acceptors.')
            return None

        print('The chosen value in the latest round is "' + str(self.accepted_value) + '".')
        return self.accepted_value


if __name__ == '__main__':
    num_acceptors = 3

    learner = Learner(num_acceptors)

    acceptors = []

    for i in range(num_acceptors):
        name = 'a' + str(i)
        learners = [learner]
        acceptor = Acceptor(name, learners)
        acceptors.append(acceptor)

    proposer1 = Proposer(acceptors)
    

    proposer1.value = 'A'
    

    for i in range(3):  # You can change the number of iterations as needed
        proposer1.send_prepare_requests()
        proposer1.send_accept_requests()



    learner.get_chosen_value()  # Get the chosen value
