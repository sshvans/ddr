import json
import math
import sys
import os


def load_file(input_file):
    with open(input_file) as data_file:
        pose_details = json.load(data_file)
    return pose_details


def individual_move(pose_points1, pose_points2):
    """
    Calculates weighted average distance between coordinates
    of a person captured in consecutive images   
    :param pose_points1: (x1, y1, c1 ...) array of person at time T1 
    :param pose_points2: (x1, y1, c1 ...) array of person at time T2 
    :return: weighted average displacement
    """

    num_points = int(min(len(pose_points1), len(pose_points2)) / 3)

    pt_distances = []
    conf_weights = []
    wt_distances = []

    for i in range(0, num_points):
        x1 = pose_points1[3 * i]
        y1 = pose_points1[3 * i + 1]
        c1 = pose_points1[3 * i + 2]

        x2 = pose_points2[3 * i]
        y2 = pose_points2[3 * i + 1]
        c2 = pose_points2[3 * i + 2]

        pt_distance = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
        sum_conf = c1 + c2
        wt_distance = sum_conf * pt_distance
        pt_distances.append(pt_distance)
        conf_weights.append(sum_conf)
        wt_distances.append(wt_distance)

    total_displacement = 0.0
    total_weighted_displacement = 0.0
    total_conf_sum = 0.0

    for i in range(0, num_points):
        total_displacement += pt_distances[i]
        total_weighted_displacement += wt_distances[i]
        total_conf_sum += conf_weights[i]

    # print("Total displacement: " + str(total_displacement))
    # print("Avg displacement: " + str(total_displacement/num_points))
    # print("Sum weighted displacement " + str(total_weighted_displacement))
    # print("Total conf sum " + str(total_conf_sum))
    # print("Average weighted displacement " + str(total_weighted_displacement/total_conf_sum))
    return total_weighted_displacement/total_conf_sum


def group_move(json1, json2):
    """
    Scores results for json captured for two consecutive images    
    :param json1: rendered json for the image at time T1     
    :param json2: rendered json for the image at time T2     
    :return: An array containing: [average group score, total group score, number of people, array of individual scores]
    """

    num_people = max(min(len(json1['people']), len(json2['people'])), 1) # Take care of divide by zero error
    pers_scores = []
    group_score = 0.0

    for i in range(0, num_people):
        pose_points1 = json1['people'][i]['pose_keypoints']
        pose_points2 = json2['people'][i]['pose_keypoints']
        pers_score = individual_move(pose_points1, pose_points2)
        pers_scores.append(pers_score)
        group_score += pers_score

    # print(num_people)
    # print("Group total: " + str(group_score))
    # print("Group average: " + str(group_score/num_people))
    # print("Individual totals: " + str(pers_scores))

    return [group_score/num_people, group_score, num_people, pers_scores]


def fetch_score(file1, file2):
    """
        Calculates average movement score between two consecutive dance image snapshots
    :param file1: Computed JSON file for dance image captured at time T1
    :param file2: Computed JSON file for dance image captured at time T2
    :return: An array containing: [average group score, total group score, number of people, array of individual scores]
    """
    pose_details1 = load_file(file1)
    pose_details2 = load_file(file2)
    return group_move(pose_details1, pose_details2)


def main(argv):
    file1 = os.path.expanduser('~') + '/dev/lib-ddr/img-test/processed/img_t1_keypoints.json'
    file2 = os.path.expanduser('~') + '/dev/lib-ddr/img-test/processed/img_t2_keypoints.json'

    group_result = fetch_score(file1, file2)

    print("Group average: " + str(group_result[0]))
    print("Total Group score: " + str(group_result[1]))
    print("Num people: " + str(group_result[2]))
    print("Individual totals: " + str(group_result[3]))

    return

if __name__ == '__main__':
    main(sys.argv[1:])

