# def DFS(start, goal, states, O, dim):
#     width, height = dim
#     Q = [start]
#     S = set()
#
#     while Q:
#         curPoint = Q.pop()
#         if curPoint == goal:
#             break
#         S.add(curPoint)
#         for n in neigbours(curPoint, width, height):
#             if n in S or n in O:
#                 continue
#             Q.append(n)
#         yield curPoint
#     yield start
#
# def BFS(network, start, goal, states, O, dim):
#     width, height = dim
#     Q = deque([start])
#     S = set()
#
#     while Q:
#         curPoint = Q.popleft()
#         S.add(curPoint)
#         for n in neigbours(curPoint, width, height):
#             if n in S or n in O:
#                 continue
#             Q.append(n)
#         if curPoint == goal:
#             break
#         yield curPoint
#     yield curPoint
#
