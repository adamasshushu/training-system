import request from './index'

// ========== 题库 ==========
export function getQuestions(params) {
  return request.get('/questions', { params })
}

export function createQuestion(data) {
  return request.post('/questions', data)
}

export function updateQuestion(id, data) {
  return request.put('/questions/' + id, data)
}

export function deleteQuestion(id) {
  return request.delete('/questions/' + id)
}

// ========== 试卷 ==========
export function getExams(params) {
  return request.get('/exams', { params })
}

export function getExamDetail(id) {
  return request.get('/exams/' + id)
}

export function createExam(data) {
  return request.post('/exams', data)
}

export function updateExam(id, data) {
  return request.put('/exams/' + id, data)
}

export function deleteExam(id) {
  return request.delete('/exams/' + id)
}

// ========== 考试作答 ==========
export function submitExam(examId, data) {
  return request.post('/exams/' + examId + '/submit', data)
}

export function getExamResults(examId) {
  return request.get('/exams/' + examId + '/results')
}

export function getStudentExams() {
  return request.get('/exams', { params: { is_published: true } })
}
