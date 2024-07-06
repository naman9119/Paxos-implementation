from collections import Counter

class Proposer:

    def __init__(self, acceptors):
        self.acceptors = acceptors
        self.number = 3
        self.value = 'B'
        self.preparing_acceptors = []

    def send_prepare_requests(self):
        print('Start sending prepare requests.')

        self.preparing_acceptors = []
        highest_res_num = -1

        for acceptor in self.acceptors:  
            print('  Send a prepare request to ' + str(acceptor) +
            ' with no = ' + str(self.number) + '.')

            try:
                response = acceptor.prepare(self.number)
            except IOError:
                print('  Failed to send a prepare request to ' + str(acceptor) + '.')
                continue

            self.preparing_acceptors.append(acceptor)

            if response is not None:  # Handle case when response is None
                res_number, res_value = response  # Unpack response
                if res_number > highest_res_num:
                    highest_res_num = res_number
                    self.value = res_value

        num_acceptors = len(self.acceptors)
        num_preparing = len(self.preparing_acceptors)

        print(str(num_preparing) + ' / ' + str(num_acceptors) + ' are preparing.')

        if num_preparing < num_acceptors // 2 + 1:
            print('Acceptors that responded to a prepare request are not majority.')
            return

        print('Finish sending prepare requests.')

    def send_accept_requests(self):
        print('Start to send accept requests.')

        for acceptor in self.preparing_acceptors:
            print('  Send an accept request to ' + str(acceptor) +
                  ' with no = ' + str(self.number) +
                  ', value = "' + str(self.value) + '".')
            try:
                acceptor.accept(self.number, self.value)
            except IOError:
                print('  Failed to send an accept request to ' + str(acceptor))

        print('Finish sending accept requests.')

class Acceptor:

    def __init__(self, name, learners):
        self.name = name
        self.learners = learners
        self.prepared_number = 1
        self.accepted_number = 2
        self.accepted_value = None

    def __str__(self):
        return self.name

    def prepare(self, proposal_number):
        if proposal_number <= self.prepared_number:
            return None

        self.prepared_number = proposal_number
        return self.accepted_number, self.accepted_value

    def accept(self, proposal_number, proposal_value):
        if proposal_number < self.prepared_number:
            return

        self.accepted_number = proposal_number
        self.accepted_value = proposal_value

        for learner in self.learners:
            learner.learn_accepted_value(
                self.name, proposal_number, proposal_value)

class Learner:

    def __init__(self, num_acceptors):
        self.num_acceptors = num_acceptors
        self.accepting_acceptors = []
        self.accepted_value = []

    def learn_accepted_value(
            self, name, proposal_number, proposal_value):
        print('  ' + str(name) + ' accepted "' +
              str(proposal_value) + '".')

        self.accepting_acceptors.append(name)
        self.accepted_value.append(proposal_value)

    def get_chosen_value(self):
        most_common, num_most_common = \
            Counter(self.accepted_value).most_common(1)[0]

        if num_most_common < self.num_acceptors // 2 + 1:  # Changed 'num_acceptors' to 'self.num_acceptors'
            print('The mostly accepted value is "' + str(most_common) + '", but not majority.')
            return None

        print('The chosen value is "' + str(most_common) + '".')
        return most_common

if __name__ == '__main__':
    num_acceptors = 3

    learner = Learner(num_acceptors)

    acceptors = []

    for i in range(num_acceptors):
        name = 'a' + str(i)
        learners = [learner]
        acceptor = Acceptor(name, learners)
        acceptors.append(acceptor)

    proposer = Proposer(acceptors)

    proposer.send_prepare_requests()  # Send prepare requests
    learner.get_chosen_value()  # Get the chosen value
